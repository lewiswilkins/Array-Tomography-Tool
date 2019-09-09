import itertools
import time
from math import sqrt

import numpy as np
from numba import njit, prange
import progressbar

from array_tomography_lib import colocalisation_result


def colocalise_pairwise(channels, channel_config):
    """For each pair of channels, perform the colocalisation given in the config
       Returns a dict of ColocolisationResults"""
    results = {}
    for channel_1, channel_2 in itertools.product(channels, 2):
        results[tuple(sorted(channel_1, channel_2))] = colocalise(channel_1, channel_2, config)
    return results


def get_operation(config, ch_1, ch_2):
    # It'll be best to key the config by the sorted pairs of channels to avoid
    # duplicate keys (i,j and j,i) and to reduce the dict to one layer
    return config.get(tuple(sorted(channel_1, channel_2)))


def colocalise(channel_1, channel_2, config):
    operation = get_operation(channel_config, channel_1, channel_2)
    if operation == "distance":
        return distance_colo(channel_1, channel_2)
    elif operation == "overlap":
        return overlap_colo(channel_1, channel_2)


def overlap_colo(channel_1, channel_2):
    """Compute an image mask for pixels that are present in both channels.
       Apply the mask to the labelled image.
       Compute the regionprops.area for the masked image.
       For each image in channel_1, divide the area of the image by the area of the masked image."""
    overlapping_pixels = get_overlap_mask(channel_1.image_labels, channel_2.image_labels)


def get_overlap_mask(image_1, image_2):
    return np.logical_and(image_1, image_2)


class Colocalisation:
    def __init__(
        self,
        channels_arr=None,
        xy_resolution=0.102,
        z_resolution=0.07,
        max_distance=0.5,
        min_overlap=25,
    ):
        if channels_arr:
            self.channels_arr = channels_arr
            self.channel_names = [channel.channel_name for channel in channels_arr]
            self.results_arr = [
                colocalisation_result.ColocalisationResult(
                    self.channels_arr[i].name,
                    self.channels_arr[i].channel_name,
                    len(self.channels_arr[i].centroids),
                    [
                        names
                        for names in self.channel_names
                        if names is not self.channels_arr[i].channel_name
                    ],
                )
                for i in range(len(channels_arr))
            ]
        self.xy_resolution = xy_resolution
        self.z_resolution = z_resolution
        self.max_distance = max_distance
        self.min_overlap = min_overlap

    def set_channels_arr(self, channels_arr):
        self.channels_arr = channels_arr

    # Runs the colocalisation code. Two options are distance or overlap
    def run_colocalisation(self):
        for i, channel_i in enumerate(self.channels_arr):
            print(f"Comparing {channel_i.name} with all other channels.")
            n_objects_i = len(channel_i.centroids)
            widgets = [
                "Progress: ",
                progressbar.Percentage(),
                " ",
                progressbar.Bar(marker=progressbar.RotatingMarker()),
                " ",
                progressbar.ETA(),
                " ",
                progressbar.FileTransferSpeed(),
            ]
            bar = progressbar.ProgressBar(
                widgets=widgets, max_value=n_objects_i, redirect_stdout=True
            ).start()
            for ii in range(n_objects_i):
                bar.update(ii + 1)
                for channel_j in self.channels_arr:
                    if channel_i.channel_name == channel_j.channel_name:
                        continue
                    if channel_i.colocalisation_types[channel_j.channel_name] == "distance":
                        centroid_i = channel_i.centroids[ii]
                        self.results_arr[i].colocalisations[ii][
                            channel_j.channel_name
                        ] = self._run_distance(centroid_i, channel_j)
                    elif channel_i.colocalisation_types[channel_j.channel_name] == "overlap":
                        coord_i = channel_i.pixel_list[ii]
                        self.results_arr[i].colocalisations[ii][
                            channel_j.channel_name
                        ] = self._run_overlap(coord_i, channel_j)
            bar.finish()

    def save_results(self, output_dir):
        for result in self.results_arr:
            result.get_results()
            result.save_to_pickle(output_dir)

    def _run_distance(self, centroid_i, channel_j):
        centroids_j = channel_j.centroids
        return self._get_best_distance(
            centroid_i, centroids_j, self.xy_resolution, self.z_resolution, self.max_distance
        )

    @staticmethod
    @njit(cache=True, fastmath=True, nogil=True)
    def _get_best_distance(
        centroids, centroids_list, xy_resolution=0.102, z_resolution=0.07, max_distance=0.5
    ):
        # Loop over all centroids in channel j and returns the closest distance
        for i in range(len(centroids_list)):
            distance = sqrt(
                pow((centroids[0] - centroids_list[i][0]) * xy_resolution, 2)
                + pow((centroids[1] - centroids_list[i][1]) * xy_resolution, 2)
                + pow((centroids[2] - centroids_list[i][2]) * z_resolution, 2)
            )

            if distance < max_distance:
                return 1
        return 0

    def _run_overlap(self, coords_i, channel_j):
        coords_list_j = channel_j.pixel_list_flat
        return self._get_overlap(
            coords_i, coords_list_j, channel_j.pixel_list_index, self.min_overlap
        )

    @staticmethod
    @njit(cache=True, fastmath=True, nogil=True, parallel=False)
    def _get_overlap(coords_i, coords_list_j, index_location, min_overlap):
        previous_index = 0
        # loop over the index locations - basically loop over objects
        for i in range(len(index_location)):
            index = index_location[i] + previous_index
            coordiante_j = coords_list_j[
                previous_index:index
            ]  # get the section of array which is curen obj
            coordiante_length = int(len(coordiante_j) / 3)
            coordiante_j_reshape = coordiante_j.reshape(
                (coordiante_length, 3)
            )  # reshape to original
            # now check how many overlap
            # - doing manually because intersect1d is not avaiblable in numba
            n_overlapping = 0
            for ii in range(len(coords_i)):
                for jj in range(ii, len(coordiante_j_reshape)):
                    match = True
                    for k in range(3):
                        if coords_i[ii][k] != coordiante_j_reshape[jj][k]:
                            match = False
                    if match:
                        n_overlapping += 1
                        jj = len(coordiante_j_reshape) - 1
            # what we really care about is the max number of overlaps between any combination
            overlap_frac = (n_overlapping / len(coords_i)) * 100
            if overlap_frac > min_overlap:
                return 1
            previous_index = index
        return 0
