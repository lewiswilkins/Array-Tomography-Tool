#!/bin/python

import argparse
import glob
import os
import re
import time
import itertools
from pandas import DataFrame, read_csv

import yaml

from array_tomography_lib import ChannelFile, colocalisation, ColocalisationResult


CHANNEL_NAMES = ["PSD", "ALZ50", "SY38"]
CACHE_DIR = ".file_cache"


def main():
    args = _parse_args()
    in_dir = args.input
    out_dir = args.output
    config_path = args.config

    config = _parse_config(config_path)
    start = time.time()
    for case_number, stack_number in get_case_stack_numbers(in_dir):
        process_stack(case_number, stack_number, config, in_dir, out_dir)

    end = time.time()

    print(f"Took {end-start}s")

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


def _parse_config(config_path: str) -> dict:
    with open(config_path) as f:
        config_dict = yaml.load(f, Loader=yaml.Loader)
    return config_dict
    # return _make_shallow_dict(config_dict)

def process_stack(
    case_number: str,
    stack_number: str,
    config: dict, 
    in_dir: str,
    out_dir: str
):
    print(f"Processing {case_number}-{stack_number}")
    channels = []
    for channel_filepath in get_channels(case_number, stack_number, in_dir):
        channel_file = ChannelFile.from_tiff(channel_filepath)
        channels.append(channel_file)

    for channel in channels:
        print(channel.channel_name)
    colocalised_results = []
    for channel_1  in channels:
        print(f"Colocalising {channel_1.channel_name} with all other channels.")
        temp_colocalised_result = ColocalisationResult.from_channel_file(channel_1)
        for channel_2 in channels:
            if channel_1.channel_name == channel_2.channel_name:
                continue
            temp_colocalised_channel = channel_1.colocalise_with(channel_2, config)
            temp_colocalised_result.add_colocalised_image(temp_colocalised_channel)
        temp_colocalised_result.calculate_combination_images()
        colocalised_results.append(temp_colocalised_result)
    
    output_results_csv(colocalised_results, out_dir, config["csv_name"])
    for result in colocalised_results:
        result.save_images(out_dir)
    del channels
    del colocalised_results

def output_results_csv(colocalised_results, out_dir, out_file_name):
    file_path = os.path.join(out_dir, out_file_name)
    if os.path.isfile(file_path):
        pd = read_csv(file_path)
        csv_dict = pd.to_dict("list")
    else:
        csv_dict = create_csv_dict(colocalised_results)
    combinations_set = set([key for key in get_combination_names(colocalised_results)])
    for result in colocalised_results:
        csv_dict["case"].append(result.case_number)
        csv_dict["stack"].append(result.stack_number)
        csv_dict["channel"].append(result.channel_name)
        csv_dict["objects"].append(len(result.original_coords))
        combination_object_count = {
            x.colocalised_with : len(x.object_list) for x in result.colocalised_images
            }
        for key in combinations_set:
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
    titles_dict = {"case" : [], "stack" : [], "channel" : [], "objects" : []}
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
                    
def get_case_stack_numbers(dir_path):
    case_stack_numbers = set()
    r = re.compile(r"^.*\/(\d+)-(stack\d+)-.*.tif")
    for filename in glob.glob(f"{dir_path}/*.tif"):
        match = r.match(filename)
        case_number, stack_number = match.group(1), match.group(2)
        case_stack_numbers.add((case_number, stack_number))

    return list(case_stack_numbers)


def get_channels(case_number, stack_number, dir_path):
    r = re.compile(rf".*/{case_number}-{stack_number}-.*\.tif")
    channels = [filepath for filepath in glob.glob(f"{dir_path}/*.tif") if r.match(filepath)]
    return channels


def load_or_compute_channel_files(case_stack_number, in_dir):
    for channel_name in CHANNEL_NAMES:
        try:
            yield load_channel_file(case_stack_number, channel_name)
        except FileNotFoundError as e:
            print("Could not load cache file, loading tif image")
            yield compute_channel_file(case_stack_number, channel_name, in_dir)


def load_channel_file(case_stack_number, channel):
    _mkdir_if_not_exists(CACHE_DIR)
    channel_name = f"{case_stack_number}-{channel}"
    temp_channel_file = channel_file.ChannelFile(name=channel_name)
    loaded_channel_file = temp_channel_file.load_from_pickle(
        file_name=os.path.join(CACHE_DIR, f"{channel_name}.pickle")
    )
    return loaded_channel_file


def compute_channel_file(case_stack_number, channel_name, in_dir):
    print(f"Preprocessing {case_stack_number}.")
    filename = os.path.join(in_dir, f"{case_stack_number}-{channel_name}.tif")
    channel = channel_file.ChannelFile(name=channel_name, file_name=filename)
    channel.get_lables()
    channel.get_regionprops()
    channel.get_centroids()
    channel.get_pixel_list()
    channel.save_to_pickle(
        file_name=os.path.join(CACHE_DIR, f"{case_stack_number}-{channel_name}.pickle")
    )
    return channel


def _make_shallow_dict(config_dict):
    """Converts the two-level deep config into a dict"""
    shallow_dict = {}
    for k1, subdict in config_dict.items():
        for k2, v in subdict.items():
            shallow_dict[tuple(sorted((k1, k2)))] = v
    return shallow_dict


def _mkdir_if_not_exists(dir_path):
    if not os.path.isdir(dir_path):
        print("Directory does not exist. Creating now!")
        os.mkdir(dir_path)


def _load_colocalisation_types(file_path):
    with open(file_path) as config_file:
        return yaml.load(config_file)


if __name__ == "__main__":
    main()
