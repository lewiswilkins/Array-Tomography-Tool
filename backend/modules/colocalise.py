import argparse
import glob
import logging
import os
import re
import time

import yaml
from pandas import DataFrame, read_csv

from lib import (ATLogger, ColocalisationResult, SegmentedFile, colocalisation,
                 segment)

logger = ATLogger(__name__)

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Compute the colocalisation between channels of input images."
    )
    parser.add_argument(
        "--input", default="test_data", help="The directory where the input files are stored."
    )
    parser.add_argument(
        "--output", default="test_data", help="The directory in which to put the output files."
    )
    parser.add_argument(
        "--print", action="store_true", help="Prints a summary of the results to screen."
    )
    parser.add_argument(
        "--config",
        default="test_data/colocalisation_types.yaml",
        help="A yaml config file mapping channel pairs to the type of colocalisation to perform",
    )
    return parser.parse_args()

def run_colocalise():
    args = _parse_args()
    in_dir = args.input
    out_dir = args.output
    config_path = args.config
    _check_dir_exists(in_dir)
    _check_dir_exists(out_dir)
    config = _parse_config(config_path)
    logger.set_config(config)
    
    start = time.time()
    for name in (get_names(in_dir)):
        process_stack(name, config, in_dir, out_dir)
    end = time.time()

    logger.log(level="info", message=f"Took {end-start}s")

def server_run_colocalisation(config: dict):
    in_dir = config["input_dir"]
    out_dir = config["output_dir"]
    _check_dir_exists(in_dir)
    _check_dir_exists(out_dir)

    case_stack_names = get_names(in_dir)
    for i,name in enumerate(case_stack_names):
        logger.log(
            level="info", message=f"{i+1}/{len(case_stack_names)}", 
            name="images_processed"
        )
        process_stack(name, config, in_dir, out_dir)
        if i+1 == len(case_stack_names):
            logger.log(
                level="info", message="Finished", name="images_processed"
            )
    

def process_stack(
    name: str,
    config: dict, 
    in_dir: str,
    out_dir: str
):

    logger.log("info", f"Processing {name}", name="case_name", fe_message=name)
    channels = []
    for channel_filepath in get_channels(name, config["channels"], in_dir):
        channel_file = SegmentedFile.from_tiff(channel_filepath)
        channels.append(channel_file)

    colocalised_results = []
    t_colocalise_s = time.time()
    for channel_1  in channels:
        logger.log(
            level="info", message=f"Colocalising {channel_1.channel_name} with all other channels.", 
            name="colocalising", fe_message=channel_1.channel_name
            )
        temp_colocalised_result = ColocalisationResult.from_channel_file(channel_1)
        for channel_2 in channels:
            if channel_1.channel_name == channel_2.channel_name:
                continue
            if config["channels"][channel_1.channel_name][channel_2.channel_name].lower() == "none":
                continue
            temp_colocalised_channel = channel_1.colocalise_with(channel_2, config)
            if temp_colocalised_channel is ValueError:
                logger.log(
                    level="warning", 
                    message=f"There seems to be a mismatch of image dimensions. Check all \
                    the images in {name} have the same number of stacks. Skipping\
                    for now.",
                    name="colocalising", fe_message="Image dimension mismatch!"
                )
                return None
            temp_colocalised_result.add_colocalised_image(temp_colocalised_channel)
        temp_colocalised_result.calculate_combination_images()
        colocalised_results.append(temp_colocalised_result)
    t_colocalise_e = time.time()
    logger.log(level="debug", message=f"Time for colocalise = {t_colocalise_e-t_colocalise_s}")
    t_output_s = time.time()
    output_results_csv(colocalised_results, out_dir, config["output_filename"])
    t_output_e = time.time()
    logger.log(level="debug", message=f"Time for output = {t_output_e-t_output_s}")

    t_save_s = time.time()
    for result in colocalised_results:
        result.save_images(out_dir)
    t_save_e = time.time()
    logger.log(level="debug", message=f"Time for save = {t_save_e-t_save_s}")


def output_results_csv(colocalised_results, out_dir, out_file_name):
    logger.log(level="info", message="Saving csv.")
    file_path = os.path.join(out_dir, out_file_name)
    if os.path.isfile(file_path):
        pd = read_csv(file_path)
        csv_dict = pd.to_dict("list")
    else:
        csv_dict = create_csv_dict(colocalised_results)
    for result in colocalised_results:
        csv_dict["name"].append(result.name)
        csv_dict["channel"].append(result.channel_name)
        csv_dict["objects"].append(len(result.original_coords))
        combination_object_count = {
            x.colocalised_with : len(x.object_list) for x in result.colocalised_images
            }
        for key in get_combination_names(colocalised_results):
            if key in combination_object_count:
                csv_dict[key].append(combination_object_count[key])
            else:
                csv_dict[key].append(0)
    csv_dataframe = DataFrame(csv_dict, columns=csv_dict.keys())
    csv_dataframe.to_csv(
        file_path,
        index=None,
        )

def create_csv_dict(colocalised_results):
    titles_dict = {"name" : [], "channel" : [], "objects" : []}
    combination_dict = {}
    for key in get_combination_names(colocalised_results):
        combination_dict[key] = []
    return {**titles_dict, **combination_dict}

def get_combination_names(colocalised_results):
    combination_names = set()
    for result in colocalised_results:
        combination_names.add(result.channel_name)
        for image in result.colocalised_images:
            combination_names.add(image.colocalised_with)
    return combination_names
                    
def get_names(dir_path):
    names = set()
    r = re.compile(r"^.*\/(.*)-.*.tif")
    for filename in glob.glob(f"{dir_path}/*.tif"):
        match = r.match(filename)
        name = match.group(1)
        names.add(name)
    return list(names)

def get_channels(name, channels, dir_path):
    channels = [f"{dir_path}/{name}-{channel}.tif" for channel in channels]
    return channels

def _check_dir_exists(dir):
    if not os.path.isdir(dir):
        logger.error(f"{dir} does not exist. Check your paths are all correct!")
        exit()

def _parse_config(config_path: str) -> dict:
    try:
        with open(config_path) as f:
            config_dict = yaml.load(f, Loader=yaml.Loader)
        return config_dict
    except FileNotFoundError:
        logger.log(level="error", message="Config file does not exist! Check the path/name are correct.")
        exit()

if __name__ == "__main__":
    run_colocalise()
