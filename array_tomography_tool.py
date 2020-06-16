#!/bin/python

import argparse
import glob
import os

import yaml

from array_tomography_lib import channel_file, colocalisation, colocalisation_result

CHANNEL_NAMES = ["PSD", "ALZ50", "SY38"]
CACHE_DIR = ".file_cache"


def main():
    args = _parse_args()
    in_dir = args.input
    out_dir = args.output
    config_path = args.config

    config = _parse_config(config_path)

    for case_stack in get_case_stack_numbers(in_dir):
        process_stack(case_stack, config, in_dir)


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


def _parse_config(config_path):
    with open(config_path) as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
    return _make_shallow_dict(config_dict)


def process_stack(case_stack, config, in_dir):
    print(f"Processing {case_stack}")
    channel_files = load_or_compute_channel_files(case_stack, in_dir)
    results = colocalisation.colocalise_pairwise(channel_files, config)
    # now print the


def get_case_stack_numbers(dir_path):
    case_stack_numbers = set()
    for filename in glob.glob(f"{dir_path}/*.tif"):
        number = filename.split("/")[-1].split(".")[0].split("-")
        number = f"{number[0]}-{number[1]}"
        case_stack_numbers.add(number)

    return list(case_stack_numbers)


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
