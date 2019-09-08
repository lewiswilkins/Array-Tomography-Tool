from ArrayTomographyLib import Colocalisation, ChannelFile
from ArrayTomographyLib import ColocalisationResult
import os
import yaml
import glob


def check_dir_exists(dir_path):
    if not os.path.isdir(dir_path):
        print("Directory does not exist. Creating now!")
        os.mkdir(dir_path)


def load_colocalisation_types(file_path):
    with open(file_path) as config_file:
        return yaml.load(config_file)


def get_stack_case_numbers(dir_path):
    stack_case_numbers = []
    for file in glob.glob(f"{dir_path}/*.pickle"):
        number = file.split("/")[-1].split(".")[0].split("-")
        number = f"{number[0]}-{number[1]}"
        stack_case_numbers.append(number)

    return list(set(stack_case_numbers))


def load_channel_files(case_stack_number, channels, in_dir):
    channels_arr = []
    for channel in channels:
        channel_name = f"{case_stack_number}-{channel}"
        temp_channel_file = channel_file.ChannelFile(name=channel_name)
        temp_channel_file = temp_channel_file.load_from_pickle(
            file_name=f"{in_dir}/{channel_name}.pickle"
        )
        temp_channel_file.centroids
        channels_arr.append(temp_channel_file)

    return channels_arr


def set_colocalisation_types(channel_files, colocalisation_types):
    for file in channel_files:
        channel = file.name.split("-")[-1]
        file.set_colocalisation_types(colocalisation_types[channel])


if __name__ == "__main__":
    print("Running colocalisation..")
    # in_dir = input("Directory containing imgage pickles: ")
    # channel_names = input("Names of channels (space separated): ")
    # channel_names = channel_names.split(" ")
    # print(channel_names)
    # out_dir = input("Output directory to store result files: ")
    # colocalisation_type_config = input("Path to colocalisatoin type config: ")

    in_dir = "Results/"
    channel_names = ["PSD", "ALZ50", "SY38"]
    out_dir = "Results/"

    colocalisation_type_config = "test/colocalisation_types.yaml"

    colocalisation_types = load_colocalisation_types(colocalisation_type_config)

    case_stack_numbers = get_stack_case_numbers(in_dir)
    for case_stack in case_stack_numbers:
        print(f"Running {case_stack}")
        channel_files = load_channel_files(case_stack, channel_names, in_dir)

        set_colocalisation_types(channel_files, colocalisation_types)

        colocalisation = Colocalisation.Colocalisation(channel_files)
        colocalisation.run_colocalisation()
        colocalisation.save_results(out_dir)
