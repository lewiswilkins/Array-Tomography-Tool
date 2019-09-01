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
    for file in glob.glob("{0}/*.pickle".format(dir_path)):
        number = file.split("/")[-1].split(".")[0].split("-")
        number = "{0}-{1}".format(number[0],number[1])
        stack_case_numbers.append(number)
    return list(set(stack_case_numbers))

def load_channel_files(case_stack_number, channels, in_dir):
    channels_arr = []
    for channel in channels:
        channel_name = "{0}-{1}".format(case_stack_number, channel)
        temp_channel_file = ChannelFile.ChannelFile(name=channel_name)
        temp_channel_file.load_from_pickle(file_name="{0}/{1}.pickle".format(in_dir, channel_name))
        channels_arr.append(temp_channel_file)

    return channels_arr
    
if __name__ == "__main__":
    print("Running colocalisation..")
    in_dir = input("Directory containing imgage pickles: ")
    channel_names = input("Names of channels (space separated): ")
    channel_names = channel_names.split(" ")
    print(channel_names)
    out_dir = input("Output directory to store result files: ")
    colocalisation_type_config = input("Path to colocalisatoin type config: ")

    # colocalisation_types = load_colocalisation_types(colocalisation_type_config)
    
    case_stack_numbers = get_stack_case_numbers(in_dir)
    # for case_stack in case_stack_numbers:
        
