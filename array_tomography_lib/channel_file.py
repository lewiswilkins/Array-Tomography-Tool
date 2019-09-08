import pickle
import sys

import numpy as np

from skimage import io, measure


class ChannelFile:
    """ ChannelFile class for Array Tomography Tool. Each instance of the File class
    will have one channels image stack in. It also stores a lot of the derived
    data."""

    def __init__(self, name, file_name=None, plugin=None):
        self.name = name
        self.channel_name = self.name.split("-")[-1]
        if file_name:
            self.file_name = file_name
            self.load_tiff(file_name)
        self.image_labels = None
        self.image_regionprops = None
        self.centroids = None
        self.pixel_list = None
        self.pixel_list_flat = None
        self.pixel_list_index = None
        self.colocalisation_types = None

    def load_tiff(self, file_name, plugin="pil"):
        self.file_name = file_name
        try:
            self.image = np.array(io.imread(file_name, plugin=plugin))
        except FileNotFoundError:
            print("File not found!")
            sys.exit()

    def get_lables(self, opt=1):
        self.image_labels = measure.label(self.image, connectivity=opt)

    def get_regionprops(self):
        try:
            self.image_regionprops = measure.regionprops(self.image_labels)
        except AttributeError:
            print("No labels present! Please call get_labels first.")
            sys.exit()

    def get_centroids(self):
        try:
            self.centroids = np.array([x.centroid for x in self.image_regionprops])
        except AttributeError:
            print("No regionprops present! Please call get_regionprops first.")
            sys.exit()

    def get_pixel_list(self):
        try:
            self.pixel_list = np.array([np.array(x.coords) for x in self.image_regionprops])
            self.pixel_list_flat = self._get_flat_array(self.pixel_list)
            self.pixel_list_index = np.array([len(x.flatten()) for x in self.pixel_list])
        except AttributeError:
            print("No regionprops present! Please call get_regionprops first.")
            sys.exit()

    def save_to_pickle(self, file_name):
        with open(file_name, "wb") as output_pickle:
            pickle.dump(self, output_pickle)

    def load_from_pickle(self, file_name):
        try:
            with open(file_name, "rb") as input_pickle:
                self = pickle.load(input_pickle)
            return self
        except FileNotFoundError:
            print(f"{file_name} does not exist. Please try another file name.")
            sys.exit()

    def set_colocalisation_types(self, colocalisation_types):
        self.colocalisation_types = colocalisation_types

    def _get_flat_array(self, array):
        print("Flattening array. Not the quickest..")
        flat_array = np.array([])
        for i in range(len(array)):
            flat_array = np.concatenate((flat_array, array[i].flatten()))
        return flat_array
