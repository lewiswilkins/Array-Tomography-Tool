# Array Tomography Tool


# Notes

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
<<<<<<< HEAD
filter the labelled image by the pixels whose values are in the set of filtered object IDs
=======
filter the labelled image by the pixels whose values are in the set of filtered object IDs
>>>>>>> ca958122c508de7b8464d0a48618f22eba882f25
