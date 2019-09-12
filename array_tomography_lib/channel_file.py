import pickle
import sys

import numpy as np

from skimage import io, measure


class ChannelFile:
    """Contains one channel's image stack and associated properties.
    Image properties are calculated on-demand"""

    def __init__(self):
        self.filename = None

        self.case_stack = case_stack
        self.channel_name = self.name.split("-")[-1]
        if file_name:
            self.file_name = file_name
            self.load_tiff(file_name)

        self._labelled_image = None
        self._labels = None
        self._props = None
        self._centroids = None

        self.colocalisation_types = None

    def load_tiff(self, file_name, plugin="pil"):
        self.file_name = file_name
        self.image = np.array(io.imread(file_name, plugin=plugin))

    @property
    def labels(self):
        if not self._image_labels:
            self._image_labels = measure.label(self.image, connectivity=1)
        return self._image_labels

    @property
    def objects(self):
        if not self._props:
            self._props = measure.regionprops(self.labels, cache=True)
        return self._props

    @property
    def centroids(self):
        # warning this might behave fuckily, if so just use object.centroid directly
        yield from (ob.centroid for ob in self.objects)

    def save_to_pickle(self, file_name):
        with open(file_name, "wb") as output_pickle:
            pickle.dump(self, output_pickle)

    def load_from_pickle(self, file_name):
        with open(file_name, "rb") as input_pickle:
            self = pickle.load(input_pickle)
        return self

    def set_colocalisation_types(self, colocalisation_types):
        self.colocalisation_types = colocalisation_types
