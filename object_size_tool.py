import argparse
from glob import glob

from array_tomography_lib import ChannelFile


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Compute the size of each object between channels of input images."
    )
    parser.add_argument(
        "--input", default="test_data", help="The directory where the input files are stored."
    )
    parser.add_argument(
        "--output", default="object_sizes.csv", help="The directory in which to put the output files."
    )

    return parser.parse_args()

def write_object_sizes(file, out_name):
    channel_file = ChannelFile.from_tiff(file)
    object_sizes = channel_file.object_sizes
    case_name = file.split("/")[-1].split(".")[0]

    with open(out_name, "a") as output_file:
        for obj in object_sizes:
            output_file.write(f"{case_name},{obj}\n")
    



if __name__ == "__main__":
    args = _parse_args()
    in_dir = args.input
    out_name = args.output

    for file in glob(f"{in_dir}/*"):
        write_object_sizes(file, out_name)



