import itertools
import time
from math import sqrt
from multiprocessing import Pool
from typing import List

import numpy as np
import progressbar
from numba import njit, prange
from PIL import Image
from skimage import measure

from array_tomography_lib import colocalisation_result


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
    method = config["channels"][channel_1.channel_name][channel_2.channel_name]
    print(f"Colocalising {channel_1.channel_name} with {channel_2.channel_name} based on {method}.")
    if method == "distance":
        xy_resolution = config["xy_resolution"]
        z_resolution = config["z_resolution"]
        max_distance = config["max_distance"]
        print(f"xy: {xy_resolution} z: {z_resolution} max dist: {max_distance}")
        return _compute_distance(
            channel_1, channel_2, xy_resolution, z_resolution, max_distance
            )
    elif method == "overlap":
        return _compute_overlap(channel_1, channel_2)


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
    min_distances = []
    start = time.time()
    for channel_1_centroid in channel_1_centroids:
        distances = _get_best_distance(
            channel_1_centroid, channel_2_centroids, xy_resolution, z_resolution
        )
        min_distance = min(distances)
        if min_distance < max_distance:
            min_distances.append(min_distances)
    end = time.time()

    
    print(f"time elapsed: {end-start}s")
    print(f"{channel_1.channel_name} and {channel_2.channel_name}: ")
    print(f"{len(channel_1_centroids)} objects in channel 1")
    print(f"Found {len(min_distances)} objects within {max_distance}")


def _get_cropped_centroids(channel, centroid, offset=10):
    cropped_image = _get_cropped_image(channel.image, centroid, offset)
    labels = measure.label(cropped_image)
    regionprops = measure.regionprops(labels)
    return regionprops.centroid


def _get_cropped_image(image, centroid, offset=10):
    rounded_centroid = np.around(centroid)
    y = rounded_centroid[1]
    x = rounded_centroid[2]
    y_max = image.shape[1]
    x_max = image.shape[2]
    x_up = _is_in_range(0, x_max, x + offset)
    x_down = _is_in_range(0, x_max, x - offset)
    y_up = _is_in_range(0, y_max, y + offset)
    y_down = _is_in_range(0, y_max, y - offset)

    return image[:, y_down:y_up, x_down:x_up]


def _is_in_range(lower, upper, value):
    if value < lower:
        return lower
    elif value > upper:
        return upper
    else:
        return value


def _calculate_distances(channel_1_centroid, channel_2_centroid_list, xy_resolution, z_resolution):
    difference = np.array(channel_2_centroid_list) - np.array(channel_1_centroid)
    difference_resolved = difference * np.array([xy_resolution, xy_resolution, z_resolution])
    distances = []
    for centroid in difference_resolved:
        distances.append((difference_resolved ** 2).sum())

    return distances


@njit(cache=True, fastmath=True)
def _calculate_distances_jit(channel_1_centroid, channel_2_centroids,
        xy_resolution=0.102, z_resolution=0.07):
    """Computes the distances between object from channel_1 and all objects in channel_2.
       Returns a numpy array of the distances."""
    difference = channel_2_centroids - channel_1_centroid
    difference_resolved = difference * np.array([xy_resolution, xy_resolution, z_resolution])
    distances = []
    for i in range(len(difference_resolved)):
        distances.append((difference_resolved**2).sum())

    return np.array(distances)

@njit(cache=True, fastmath=True, nogil=True)
def _get_best_distance(
        centroids, centroids_list, xy_resolution=0.102, z_resolution=0.07
    ):
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
    overlapping_parts_ch1 = np.ma.masked_array(channel_1_image, mask=~overlapping_pixels)
    overlapping_regions = measure.regionprops(overlapping_parts_ch1)
    overlaps = []
    for region, overlap in zip(channel_1.objects, overlapping_regions):
        overlap_fraction = overlap.area / region.area
        if overlap_fraction >= min_overlap:
            overlaps.append((region.label, overlap_fraction))

    # add function here to get image with original objects but only if they overlap
    colocalised_image = _get_colocalised_image(
        channel_1_image, [x[0] for x in overlaps], channel_1.object_coords
        )

    print(f"{channel_1.channel_name} and {channel_2.channel_name}: ")
    print(f"{len(channel_1.objects)} objects in channel 1")
    print(f"Found {len(overlaps)} overlapping objects")
    print(f"mean overlap is {sum(overlaps[0])/len(overlaps)}")

    return colocalised_image, overlaps


def _get_colocalised_image(original_image, label_list, object_coords):
    colocalised_image = original_image
    colocalised_image.fill(0)

    for label in label_list:
        coords = object_coords[label]
        for pixel in coords:
            colocalised_image[pixel[0]][pixel[1]][pixel[2]] = 1
    
    return colocalised_image


    # One option is to loop over each pixel in the image, and set it to
    # zero unless it's in the set of labels. This woule be a good
    # candidate for that cool JIT thing. Looking up values in a set
    # is quick but maybe not quick enough for this, so it might be quicker
    # to loop over all the coordinates of the pixels of the objects and set
    # them in a new image. This method involves computing and storing the coordinates
    # of the objects which will also be slow. We could implement both methods
    # and compare.
 


def _get_overlap_mask(image_1, image_2):
    return np.logical_and(image_1, image_2)


# class Colocalisation:
#     def __init__(
#         self,
#         channels_arr=None,
#         xy_resolution=0.102,
#         z_resolution=0.07,
#         max_distance=0.5,
#         min_overlap=25,
#     ):
#         if channels_arr:
#             self.channels_arr = channels_arr
#             self.channel_names = [channel.channel_name for channel in channels_arr]
#             self.results_arr = [
#                 colocalisation_result.ColocalisationResult(
#                     self.channels_arr[i].name,
#                     self.channels_arr[i].channel_name,
#                     len(self.channels_arr[i].centroids),
#                     [
#                         names
#                         for names in self.channel_names
#                         if names is not self.channels_arr[i].channel_name
#                     ],
#                 )
#                 for i in range(len(channels_arr))
#             ]
#         self.xy_resolution = xy_resolution
#         self.z_resolution = z_resolution
#         self.max_distance = max_distance
#         self.min_overlap = min_overlap

#     def set_channels_arr(self, channels_arr):
#         self.channels_arr = channels_arr

#     # Runs the colocalisation code. Two options are distance or overlap
#     def run_colocalisation(self):
#         for i, channel_i in enumerate(self.channels_arr):
#             print(f"Comparing {channel_i.name} with all other channels.")
#             n_objects_i = len(channel_i.centroids)
#             widgets = [
#                 "Progress: ",
#                 progressbar.Percentage(),
#                 " ",
#                 progressbar.Bar(marker=progressbar.RotatingMarker()),
#                 " ",
#                 progressbar.ETA(),
#                 " ",
#                 progressbar.FileTransferSpeed(),
#             ]
#             bar = progressbar.ProgressBar(
#                 widgets=widgets, max_value=n_objects_i, redirect_stdout=True
#             ).start()
#             for ii in range(n_objects_i):
#                 bar.update(ii + 1)
#                 for channel_j in self.channels_arr:
#                     if channel_i.channel_name == channel_j.channel_name:
#                         continue
#                     if channel_i.colocalisation_types[channel_j.channel_name] == "distance":
#                         centroid_i = channel_i.centroids[ii]
#                         self.results_arr[i].colocalisations[ii][
#                             channel_j.channel_name
#                         ] = self._run_distance(centroid_i, channel_j)
#                     elif channel_i.colocalisation_types[channel_j.channel_name] == "overlap":
#                         coord_i = channel_i.pixel_list[ii]
#                         self.results_arr[i].colocalisations[ii][
#                             channel_j.channel_name
#                         ] = self._run_overlap(coord_i, channel_j)
#             bar.finish()

#     def save_results(self, output_dir):
#         for result in self.results_arr:
#             result.get_results()
#             result.save_to_pickle(output_dir)

#     def _run_distance(self, centroid_i, channel_j):
#         centroids_j = channel_j.centroids
#         return self._get_best_distance(
#             centroid_i, centroids_j, self.xy_resolution, self.z_resolution, self.max_distance
#         )

#     @staticmethod
#     @njit(cache=True, fastmath=True, nogil=True)
#     def _get_best_distance(
#         centroids, centroids_list, xy_resolution=0.102, z_resolution=0.07, max_distance=0.5
#     ):
#         # Loop over all centroids in channel j and returns the closest distance
#         for i in range(len(centroids_list)):
#             distance = sqrt(
#                 pow((centroids[0] - centroids_list[i][0]) * xy_resolution, 2)
#                 + pow((centroids[1] - centroids_list[i][1]) * xy_resolution, 2)
#                 + pow((centroids[2] - centroids_list[i][2]) * z_resolution, 2)
#             )

#             if distance < max_distance:
#                 return 1
#         return 0

#     def _run_overlap(self, coords_i, channel_j):
#         coords_list_j = channel_j.pixel_list_flat
#         return self._get_overlap(
#             coords_i, coords_list_j, channel_j.pixel_list_index, self.min_overlap
#         )

#     @staticmethod
#     @njit(cache=True, fastmath=True, nogil=True, parallel=False)
#     def _get_overlap(coords_i, coords_list_j, index_location, min_overlap):
#         previous_index = 0
#         # loop over the index locations - basically loop over objects
#         for i in range(len(index_location)):
#             index = index_location[i] + previous_index
#             coordiante_j = coords_list_j[
#                 previous_index:index
#             ]  # get the section of array which is curen obj
#             coordiante_length = int(len(coordiante_j) / 3)
#             coordiante_j_reshape = coordiante_j.reshape(
#                 (coordiante_length, 3)
#             )  # reshape to original
#             # now check how many overlap
#             # - doing manually because intersect1d is not avaiblable in numba
#             n_overlapping = 0
#             for ii in range(len(coords_i)):
#                 for jj in range(ii, len(coordiante_j_reshape)):
#                     match = True
#                     for k in range(3):
#                         if coords_i[ii][k] != coordiante_j_reshape[jj][k]:
#                             match = False
#                     if match:
#                         n_overlapping += 1
#                         jj = len(coordiante_j_reshape) - 1
#             # what we really care about is the max number of overlaps between any combination
#             overlap_frac = (n_overlapping / len(coords_i)) * 100
#             if overlap_frac > min_overlap:
#                 return 1
#             previous_index = index
#         return 0
