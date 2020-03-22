import pickle
import sys
from typing import List
import os
# import functools
from cached_property import cached_property

import numpy as np
from skimage import io, measure

from array_tomography_lib import colocalisation


class ChannelFile:
    """Contains one channel's image stack and associated properties.
    Image properties are calculated on-demand"""

    def __init__(
        self,
        image: np.ndarray,
        name: str,
        channel_name: str,
    ):
        self.image = image
        self.name = name
        self.channel_name = channel_name
        self._labelled_image = None
        self._objects = None
        self._labels = None
        self._centroids = None
        self._object_coords = None
        self._object_sizes = None

    @classmethod
    def from_tiff(cls, file_path):
        # will need to try to load from pickle cache first
        image = np.array(io.imread(file_path, plugin="tifffile"), dtype=np.int16)
        file_name = cls._split_file_path(file_path)
        name, channel_name = cls._split_file_name(file_name)
        return cls(image, name, channel_name)

    @classmethod
    def _split_file_path(cls, file_path):
        file_name = file_path.rsplit("/", 1)[-1].split(".")[0]
        return file_name

    @classmethod
    def _split_file_name(cls, file_name):
        channel_name = file_name.split("-")[-1]
        name = "-".join(file_name.split("-")[:-1])
        return name, channel_name

    @cached_property
    def labelled_image(self):
        self._labelled_image = np.array(measure.label(
            self.image, connectivity=1
        )) 
        return self._labelled_image

    @cached_property
    def labels(self):
        self._labels = [ob.label for ob in self.objects]
        return self._labels

    @cached_property
    def objects(self):
        self._objects = measure.regionprops(self.labelled_image, cache=False)
        return self._objects

    @cached_property
    def centroids(self):
        self._centroids = np.array([ob.centroid for ob in self.objects])
        return self._centroids

    @cached_property
    def object_coords(self):
        self._object_coords = np.array([ob.coords for ob in self.objects])
        return self._object_coords
    
    @cached_property
    def object_sizes(self):
        self._object_sizes = np.array([ob.area for ob in self.objects])
        return self._object_sizes

    def colocalise_with(self, other_channel, config):
        colocalised_image, object_list = colocalisation.colocalise(self, other_channel, config)
        
        if colocalised_image is ValueError:
            return object_list
        
        colocalisation_channel_file = ColocalisedChannelFile(
            image=colocalised_image,
            name=self.name,
            channel_name=self.channel_name,
            colocalised_with=other_channel.channel_name,
            object_list=object_list,
        )

        return colocalisation_channel_file

    # we need to save the file with a unique name for each image/config combination. to be done with checksum
    def save_to_pickle(self, file_name):
        with open(file_name, "wb") as output_pickle:
            pickle.dump(self, output_pickle)

    @classmethod
    def load_from_pickle(cls, file_name):
        with open(file_name, "rb") as input_pickle:
            self = pickle.load(input_pickle)
        return self

    def set_colocalisation_types(self, colocalisation_types):
        self.colocalisation_types = colocalisation_types


class ColocalisedChannelFile(ChannelFile):
    def __init__(
        self,
        image: np.ndarray,
        name: str,
        channel_name: str,
        colocalised_with: str,
        object_list: dict,
    ):
        super().__init__(image, name, channel_name)
        self.colocalised_with = colocalised_with
        self.object_list = object_list
        self.output_file_name = f"{self.name}-{self.channel_name}{self.colocalised_with}.tif"
        self.image = np.array(self.image, dtype=np.int16)
    
    def save_to_tiff(self, out_dir, out_file_name=None):
        if out_file_name is None:
            out_file_name = self.output_file_name
        io.imsave(
            os.path.join(out_dir, out_file_name),
            self.image, 
            plugin="tifffile",
            check_contrast=False
        )

