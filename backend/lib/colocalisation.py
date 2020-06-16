import itertools
import time
from math import sqrt
from typing import List

import numpy as np
from numba import njit
from skimage import measure

from lib import utils


def colocalise_pairwise(channels, config):
    """Computes the colocalisation for each pair of channels, according to the method.
        Args:
            channels: A list of ChannelFile
            config: a dict whose keys are (channel_1, channel_2) tuples and whose values are the
                    method of colocalisation to perform, either 'distance' or 'overlap'
       Returns: a dict of (channel_1, channel_2) -> ColocolisationResult"""

    results = {}
    for channel_1, channel_2 in itertools.product(channels, repeat=2):
        if channel_1 == channel_2:
            continue
        method = _read_config(config, channel_1.channel_name, channel_2.channel_name)
        results[tuple(sorted((channel_1.name, channel_2.name)))] = colocalise(
            channel_1, channel_2, method
        )
    return results


def colocalise(channel_1, channel_2, config):
    """Computes the colocalisation for a pair of channels with the given method.
        Args:
            channel_1: ChannelFile
            channel_2: ChannelFile
            method: the type of colocalisation to perform, either either 'distance' or 'overlap'
       Returns:
            a pair of images which only contain the colocalised objects, and a map of
            object -> overlap fraction """
    channel_1_name = channel_1.channel_name
    channel_2_name = channel_2.channel_name
    try:
        method = config["channels"][channel_1.channel_name][channel_2.channel_name]
    except KeyError as err:
        print(f"Cannot get method for {channel_2.channel_name}. Check your config,"\
    f" you probably havent set a method for {channel_2.channel_name}.")
        exit()
    print(f"Colocalising {channel_1.channel_name} with {channel_2.channel_name} based on {method}.")
    print(f"{len(channel_1.objects)} objects in {channel_1_name}")
    print(f"{len(channel_2.objects)} objects in {channel_2_name}\n")
    if method.lower() == "distance":
        xy_resolution = config["xy_resolution"]
        z_resolution = config["z_resolution"]
        max_distance = config["max_distance"]
        return _compute_distance(
            channel_1, channel_2, xy_resolution, z_resolution, max_distance
            )
    elif method.lower() == "overlap":
        return _compute_overlap(channel_1, channel_2, min_overlap=config["min_overlap"])


def _read_config(config, channel_1, channel_2):
    # It'll be best to key the config by the sorted pairs of channels to avoid
    # duplicate keys (i,j and j,i) and to reduce the dict to one layer
    return config[tuple(sorted((channel_1, channel_2)))]


def _compute_distance(
    channel_1, channel_2, xy_resolution=0.102, z_resolution=0.07, max_distance=0.5
):
    """Compute the distances between each object in channel_1 and channel_2.
       Find the number of objects in channel_1 which are within max_distance of
       channel_2."""
    
    channel_1_centroids = channel_1.centroids
    channel_2_centroids = channel_2.centroids
    min_distances = {}


    for region,channel_1_centroid in zip(channel_1.objects, channel_1_centroids):
        distances = _calculate_distances(
            channel_1_centroid, channel_2_centroids, xy_resolution, z_resolution
        )
        min_distance = min(distances)
        if min_distance < max_distance:
            min_distances[region.label] = {f"{channel_2.channel_name}_distance" : min_distances}
    
    colocalised_image = get_colocalised_image(
        channel_1.image, min_distances, channel_1.object_coords
        )

    print(f"{channel_1.channel_name} and {channel_2.channel_name}: ")
    print(f"{len(channel_1_centroids)} objects in channel 1")
    print(f"Found {len(min_distances)} objects within {max_distance}\n")

    return colocalised_image, min_distances


@njit(cache=True, fastmath=True)
def _calculate_distances(
        centroids, centroids_list, xy_resolution=0.102, z_resolution=0.07
    ):
    """Computes the distances between object from channel_1 and all objects in channel_2.
       Returns a numpy array of the distances."""
    distances = []
    # Loop over all centroids in channel j and returns the closest distance
    for i in range(len(centroids_list)):
        distance = sqrt(
            pow((centroids[0] - centroids_list[i][0]) * xy_resolution, 2)
            + pow((centroids[1] - centroids_list[i][1]) * xy_resolution, 2)
            + pow((centroids[2] - centroids_list[i][2]) * z_resolution, 2)
        )
        distances.append(distance)
    
    return np.array(distances)


def _compute_overlap(channel_1, channel_2, min_overlap=0.25):
    """Compute an image mask for pixels that are present in both channels.
       Apply the mask to the labelled image.
       Compute the regionprops.area for the masked image.
       For each image in channel_1, divide the area of the image by the area of the masked image.

       Create a tuple of (region id, overlap fraction) for overlapping regions
       in each channel"""
    channel_1_image = channel_1.labelled_image
    channel_2_image = channel_2.labelled_image
    overlapping_pixels = _get_overlap_mask(channel_1_image, channel_2_image)
    if overlapping_pixels is ValueError:
        return overlapping_pixels, overlapping_pixels
    overlapping_parts_ch1 = np.ma.masked_array(channel_1_image, mask=~overlapping_pixels)
    overlapping_regions = measure.regionprops(overlapping_parts_ch1)
    overlaps = {}
    for region, overlap in zip(channel_1.objects, overlapping_regions):
        overlap_fraction = overlap.area / region.area
        if overlap_fraction >= min_overlap:
            overlaps[region.label] = {f"{channel_2.channel_name}_overlap" : overlap_fraction}

    # add function here to get image with original objects but only if they overlap
    colocalised_image = get_colocalised_image(
        channel_1_image, overlaps, channel_1.object_coords
        )
    print(f"{channel_1.channel_name} and {channel_2.channel_name}: ")
    print(f"{len(channel_1.objects)} objects in channel 1")
    print(f"Found {len(overlaps)} overlapping objects")
    if len(overlaps) > 0:
        print(f"mean overlap is {sum(overlaps)/len(overlaps)}\n")
    else:
        print("No overlaps found!")
    return colocalised_image, overlaps


def get_colocalised_image(original_image, label_list, object_coords):
    colocalised_image = np.copy(original_image)
    colocalised_image.fill(0)
    for label in label_list: 
        coords = object_coords[label-1]
        utils.set_pixels(colocalised_image, coords, 1)

    return colocalised_image
    
def _get_overlap_mask(image_1, image_2):
    try:
        return np.logical_and(image_1, image_2)
    except ValueError as err:
        print("Images do not have the same dimensions. Please check and retry.")
        return err
