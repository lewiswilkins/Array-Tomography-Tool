# Array Tomography Tool
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/lewiswilkins/array_tomography_tool)
## Running Array Tomography Tool

The easiest method to running the tool is to use Docker. First you will require
Docker installed on your computer - go to
https://www.docker.com/products/docker-desktop to download and install.

Then you need to get the Docker image for the tool. Go to your terminal then
paste in the following command


`docker pull lewiswilkins/array_tomography_tool:v0.2.1`


This will probably take a couple of mins to download. Once complete, you are
ready to run the tool. For now it only does the colocalisation. The tool takes 3
arguments:
- `--input` the directory with the input files 
- `--output` the output directory
- `--config` the `.yaml` config file containing the colocalisation parameters

An example of the config file can be found in this repo - `example_config.yaml`.
To run the tool, you will use the following command:


`docker run -it -v /path/to/files/:/mnt/files/ lewiswilkins/array_tomography_tool:v0.2.1  --input
/mnt/files/inputs/ --output /mnt/files/output/ --config /mnt/files/config.yaml`

Here you will need to replace `/path/to/files/` with the path to wherever your
input files are. The suggested setup is to have a folder with two folders in it.
One called `inputs` which will contain all of the input images you wish to run
over. Another called `output` which will store the output images and numbers.
You should also put your config file in this directory.


## Notes

Design around the ChannelFile class, which contains derived properties about the channel,
for example number of objects, object areas, colocalised objects etc.
In a similar way to measure.regionprops, we can use the property decorator and caching to
compute derived properties when they're first needed, caching the results to file so that
when they're needed again they're not recomputed.

We should cache. The colocalisation may be re run with different max distance or
min overlap parameters.

The rest of the program then just instantiates the ChannelFile objects, and gets whichever
properties it needs at the point at which it wants to use them.

## Workflow

`array_tomography_tool` inputs:
- `--input` the directory with the input files 
- `--output` the output directory
- `--config` the `.yaml` config file containing the colocalisation parameters

The tool runs over a directory of images which contains images from different
cases. For each case there will also be a number of stacks.
Then for each stack there are *N* channels. The colocalisation between each of
the *N* channels is calculated for each unique case and stack combination.

Each unique case-stack combination is looped over and the files for each channel
are preprocessed. If this is the first time the files have been used, a cache is
made. Otherwise the cache will be loaded to save processing time. (Is this still
useful if we are calling the objects at run time?)


### Colocalisation:
In each ChannelFile for each object, label which channels the object overlaps with and by how much.

to produce a colocalised image, filter the list of objects by those which fit the conditions, then
filter the labelled image by the pixels whose values are in the set of filtered object IDs
