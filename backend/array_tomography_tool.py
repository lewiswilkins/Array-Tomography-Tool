#!/bin/python

import argparse
import glob
import os
import re
import time
import itertools
import multiprocessing
from pandas import DataFrame, read_csv
import gc 
from pathlib import Path
import logging


import yaml

from array_tomography_lib import ChannelFile, colocalisation, ColocalisationResult, segment


CACHE_DIR = ".file_cache"

logger = logging.getLogger(__name__)


def log(config: dict, log_file: str, value):
    """Wirite the frontend logs."""
    if "job_id" in config:
        job_id = config["job_id"]
        if not Path(f"/tmp/{job_id}").exists():
            Path(f"/tmp/{job_id}").mkdir()
        Path(f"/tmp/{job_id}/{log_file}.out").write_text(value)


def server_run_colocalisation(config: dict):
    in_dir = config["input_dir"]
    out_dir = config["output_dir"]
    _check_dir_exists(in_dir)
    _check_dir_exists(out_dir)

    case_stack_names = get_names(in_dir)
    for i,name in enumerate(case_stack_names):
        log(config, "images_processed", f"{i+1}/{len(case_stack_names)}")
        process_stack(name, config, in_dir, out_dir)
        if i+1 == len(case_stack_names):
            log(config, "images_processed", "Finished!")

def server_run_segment(config: dict):
    input_dir = config["input_dir"]
    output_dir = config["output_dir"]
    file_pattern = config["files"]
    threshold_method = config["thresholdMethod"]
    threshold_params = config["thresholdParams"]
    _check_dir_exists(input_dir)
    _check_dir_exists(output_dir)

    for i, file_name in enumerate(glob.glob(f"{input_dir}/{file_pattern}")):
        # log(config, "segment_images_processed", f"{i+1}/{len(case_stack_names)}")
        channel_file = ChannelFile.from_tiff(file_name)
        segment.threshold_stack(channel_file, threshold_method, threshold_params)


def main():
    args = _parse_args()
    in_dir = args.input
    out_dir = args.output
    config_path = args.config
    _check_dir_exists(in_dir)
    _check_dir_exists(out_dir)
    processes = args.processes
    if processes == 0:
        processes = multiprocessing.cpu_count()

    config = _parse_config(config_path)
    start = time.time()
    
    if processes == 1:
        for name in (get_names(in_dir)):
            process_stack(name, config, in_dir, out_dir)
    else:
        p = multiprocessing.Pool(processes=processes)
        args = ((name, config, in_dir, out_dir) for name in get_names(in_dir))
        p.starmap(process_stack, args)
    

    end = time.time()
    logger.info(f"Took {end-start}s")

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
    parser.add_argument(
        "--processes",
        default=1,
        help="The number of processes to use.",
        type=int,

    )
    return parser.parse_args()

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
        logger.error("Config file does not exist! Check the path/name are correct.")
        exit()





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
