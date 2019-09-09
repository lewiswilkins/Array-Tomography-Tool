import glob
import os

from array_tomography_lib import channel_file


def check_dir_exists(dir_path):
    if not os.path.isdir(dir_path):
        print("Directory does not exist. Creating now!")
        os.mkdir(dir_path)


if __name__ == "__main__":
    print("Processing image stacks..")
    # File list to be processed, what options, output to pickle
    # Do we glob a dir? need output dir etc.
    in_dir = input("Directory containing imgage stacks: ")
    out_dir = input("Output directory to store pickle files: ")
    check_dir_exists(out_dir)

    image_stacks = glob.glob(f"{in_dir}/*.tif")

    for stack in image_stacks:
        stack_name = stack.split("/")[-1].split(".")[0]
        print(f"Processing {stack_name}.")
        channel = channel_file.ChannelFile(name=stack_name, file_name=stack)
        channel.get_lables()
        channel.get_regionprops()
        channel.get_centroids()
        channel.get_pixel_list()

        channel.save_to_pickle(file_name=f"{out_dir}/{stack_name}.pickle")
