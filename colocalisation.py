import argparse
import glob
import os

import yaml

from array_tomography_lib import channel_file, colocalisation, colocalisation_result

CHANNEL_NAMES = {"PSD", "ALZ50", "SY38"}
WORKING_DIR = "test_data"


def main():
    print("Running colocalisation")

    # args = parse_args()
    # in_dir = args.input
    # out_dir = args.output
    # config_path = args.config

    # config = parse_config(config_path)
    # print(config)

    # for case_stack in get_stack_case_numbers(in_dir):
    #     process_stack(case_stack, config, in_dir)


def process_stack(case_stack, config, in_dir):
    print(f"Processing {case_stack}")
    channel_files = list(load_or_compute_channel_files(case_stack, in_dir))
    colocalisation.colocalise_pairwise(channel_files, config)


#     set_colocalisation_types(channel_files, colocalisation_types)
#     colo = colocalisation.Colocalisation(channel_files)
#     colo.run_colocalisation()
#     colo.save_results(out_dir)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute the colocalisation between channels of input images."
    )
    parser.add_argument("--input", default="test_data", help="A directory to read input files from")
    parser.add_argument("--output", default="test_data", help="A directory to store output data")
    parser.add_argument(
        "--config",
        default="test_data/colocalisation_types.yaml",
        help="A yaml config file mapping channel pairs to the type of colocalisation to perform",
    )
    return parser.parse_args()


def parse_config(config_path):
    with open(config_path) as f:
        config_dict = yaml.load(f)
    return make_shallow_dict(config_dict)


def make_shallow_dict(config_dict):
    """Converts the two-level deep config into a dict"""
    shallow_dict = {}
    for k1, subdict in config_dict.items():
        for k2, v in subdict.items():
            shallow_dict[tuple(sorted((k1, k2)))] = v
    return shallow_dict


def check_dir_exists(dir_path):
    if not os.path.isdir(dir_path):
        print("Directory does not exist. Creating now!")
        os.mkdir(dir_path)


def load_colocalisation_types(file_path):
    with open(file_path) as config_file:
        return yaml.load(config_file)


def get_stack_case_numbers(dir_path):
    stack_case_numbers = set()
    for filename in glob.glob(f"{dir_path}/*.pickle"):
        number = filename.split("/")[-1].split(".")[0].split("-")
        number = f"{number[0]}-{number[1]}"
        stack_case_numbers.add(number)

    return list(stack_case_numbers)


def load_or_compute_channel_files(case_stack_number, in_dir):
    for channel_name in CHANNEL_NAMES:
        try:
            channel_data = load_channel_file(case_stack_number, channel_name, in_dir)
        except Exception:
            channel_data = compute_channel_file(case_stack_number, channel_name)
        yield channel_data


def load_channel_file(case_stack_number, channel, in_dir):
    channel_name = f"{case_stack_number}-{channel}"
    temp_channel_file = channel_file.ChannelFile(name=channel_name)
    loaded_channel_file = temp_channel_file.load_from_pickle(
        file_name=os.path.join(in_dir, f"{channel_name}.pickle")
    )
    return loaded_channel_file


def compute_channel_file(case_stack_number, channel_name):
    print(f"Preprocessing {case_stack_number}.")
    channel = channel_file.ChannelFile(name=case_stack_number, file_name=stack)
    channel.get_lables()
    channel.get_regionprops()
    channel.get_centroids()
    channel.get_pixel_list()
    return channel


def set_colocalisation_types(channel_files, colocalisation_types):
    for file in channel_files:
        channel = file.name.split("-")[-1]
        file.set_colocalisation_types(colocalisation_types[channel])


if __name__ == "__main__":
    main()
