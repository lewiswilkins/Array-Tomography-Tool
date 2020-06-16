# Array Tomography Tool


# Notes

Design around the ChannelFile class, which contains derived properties about the channel,
for example number of objects, object areas, colocalised objects etc.
In a similar way to measure.regionprops, we can use the property decorator and caching to
compute derived properties when they're first needed, caching the results to file so that
when they're needed again they're not recomputed.

The rest of the program then just instantiates the ChannelFile objects, and gets whichever
properties it needs at the point at which it wants to use them.

### Colocalisation:
In each ChannelFile for each object, label which channels the object overlaps with and by how much.

to produce a colocalised image, filter the list of objects by those which fit the conditions, then
filter the labelled image by the pixels whose values are in the set of filtered object IDs
