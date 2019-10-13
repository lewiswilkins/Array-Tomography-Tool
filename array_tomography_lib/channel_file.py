import pickle
import sys

import numpy as np
from skimage import io, measure

from array_tomography_lib import colocalisation


class ChannelFile:
    """Contains one channel's image stack and associated properties.
    Image properties are calculated on-demand"""

    def __init__(
        self,
        image: np.ndarray,
        case_number: str,
        stack_number: str,
        channel_name: str,
    ):
        self.image = image
        self.case_number = case_number
        self.stack_number = stack_number
        self.channel_name = channel_name
        self._labelled_image = None
        self._objects = None
        self._labels = None
        self._centroids = None
        self._object_coords = None

    @classmethod
    def from_tiff(cls, file_path):
        # will need to try to load from pickle cache first
        image = np.array(io.imread(file_path, plugin="pil"))
        file_name = cls._split_file_path(file_path)
        case_number, stack_number, channel_name = cls._split_file_name(file_name)
        return cls(image, case_number, stack_number, channel_name)

    @classmethod
    def _split_file_path(cls, file_path):
        file_name = file_path.rsplit("/", 1)[-1].split(".")[0]

        return file_name

    @classmethod
    def _split_file_name(cls, file_name):
        case_number, stack_number, channel_name = file_name.split("-")

        return case_number, stack_number, channel_name

    @property
    def labelled_image(self):
        if self._labelled_image is None:
            self._labelled_image = np.array(measure.label(
                self.image, connectivity=1
            ))
            
        return self._labelled_image

    @property
    def labels(self):
        if not self._labels:
            self._labels = [ob.label for ob in self.objects]
        return self._labels

    @property
    def objects(self):
        if not self._objects:
            self._objects = measure.regionprops(self.labelled_image, cache=False)
        return self._objects


    @property
    def centroids(self):
        if not self._centroids:
            self._centroids = np.array([ob.centroid for ob in self.objects])
        return self._centroids


    @property
    def object_coords(self):
        if self._object_coords is None:
            self._object_coords = np.array([ob.coords for ob in self.objects])
        return self._object_coords


    def colocalise_with(self, other_channel, config):
        colocalised_image, object_list = colocalisation.colocalise(self, other_channel, config)

        colocalisation_channel_file = ColocalisedChannelFile(
            image=colocalised_image,
            case_number=self.case_number,
            stack_number=self.stack_number,
            channel_name=self.channel_name,
            colocalised_with=other_channel.channel_name,
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
        case_number: str,
        stack_number: str,
        channel_name: str,
        colocalised_with: str,
    ):
        super().__init__(image, case_number, stack_number, channel_name)
        self.colocalised_with = colocalised_with
        self.overlap_list = None
        self.distance_list = None
        self.colocalisation_method = None
