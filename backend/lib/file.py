import pickle
import sys
from typing import List
import os
from cached_property import cached_property

import numpy as np
from skimage import io, measure

from lib import colocalisation


class File:
    """Base file class to handle images"""

    def __init__(
        self,
        image: np.ndarray,
        name: str,
        channel_name: str,
    ):
        self.image = image
        self.name = name
        self.channel_name = channel_name
        self.output_file_name = None

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

    def save_to_tiff(self, output_dir, output_file_name=None):
        self.image = np.array(self.image, dtype=np.int16)
        if output_file_name is None:
            output_file_name = self.output_file_name
        io.imsave(
            os.path.join(output_dir, output_file_name),
            self.image, 
            plugin="tifffile",
            check_contrast=False
        )


class SegmentedFile(File):
    """File class to store segmented images"""

    def __init__(
        self,
        image: np.ndarray,
        name: str,
        channel_name: str
    ):
        super().__init__(image, name, channel_name)
        self.output_file_name = f"{self.name}-segmented-{self.channel_name}.tif"
        self.connectivity = 1
        self.labelled_image = np.array(
            measure.label(self.image, connectivity=self.connectivity)
        )
        self._objects = None
        self._labels = None
        self._centroids = None
        self._object_coords = None

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

    def colocalise_with(self, other_channel, config):
        colocalised_image, object_list = colocalisation.colocalise(self, other_channel, config)
        if colocalised_image is ValueError:
            return object_list
        
        colocalisation_channel_file = ColocalisedFile(
            image=colocalised_image,
            name=self.name,
            channel_name=self.channel_name,
            colocalised_with=other_channel.channel_name,
            object_list=object_list,
        )

        return colocalisation_channel_file

    def set_connectivity(self, connectivity: int) -> None:
        self.connectivity = connectivity
        self.labelled_image

    def save_to_tiff(
        self, output_dir: str, output_file_name: str = None, 
        labelled_image: bool = False
    ) -> None:
        self.image = np.array(self.image, dtype=np.int16)
        image_to_save = self.labelled_image if labelled_image else self.image 
        if output_file_name is None:
            output_file_name = self.output_file_name
        io.imsave(
            os.path.join(output_dir, output_file_name),
            image_to_save, 
            plugin="tifffile",
            check_contrast=False
        )

class ColocalisedFile(File):
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