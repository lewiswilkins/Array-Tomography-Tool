import pickle
import itertools
import functools
import numpy as np

from array_tomography_lib import ColocalisedChannelFile, colocalisation



class ColocalisationResult:
    """The colocalisations for one image stack. Contains a list of all colocalisation
     possibilities for every subset of channels"""
    
    def __init__(
        self,
        name: str,
        channel_name: str,
        original_coords=None,
        original_image=None
    ):
        self.name = name
        self.channel_name = channel_name
        self.colocalised_images = []
        self.original_coords = original_coords
        self.original_image = original_image
    @classmethod
    def from_channel_file(cls, channel_file):
        return cls(
            name=channel_file.name,
            channel_name=channel_file.channel_name,
            original_coords=channel_file.object_coords,
            original_image=channel_file.image
        )

    def add_colocalised_image(self, colocalised_image: ColocalisedChannelFile):
        self.colocalised_images.append(colocalised_image)
        # print(f"There are {len(self.colocalised_images)} in the object.")
    
    def calculate_combination_images(self):
        for x in range(2, len(self.colocalised_images) + 1):
            for combination in itertools.combinations(self.colocalised_images, x):
                object_lists = (image.object_list for image in combination)
                combined_object_list = functools.reduce(self._combine_dicts, object_lists)
                combined_image = colocalisation.get_colocalised_image(
                    original_image=self.original_image,
                    label_list=combined_object_list,
                    object_coords=self.original_coords
                )
                temp_colocalised_channel_file = ColocalisedChannelFile(
                    image=combined_image,
                    name=self.name,
                    channel_name=self.channel_name,
                    colocalised_with=self._get_colocalised_with_string(combination),
                    object_list=combined_object_list
                )
            self.colocalised_images.append(temp_colocalised_channel_file)
    
    def save_images(self, out_dir):
        for image in self.colocalised_images:
            if image.image is not None:
                image.save_to_tiff(out_dir)
    
    def _get_colocalised_with_string(self, images):
        colocalised_with_string = ""
        for image in images:
            colocalised_with_string += image.colocalised_with 
        return colocalised_with_string

    def _combine_dicts(self, dict_1, dict_2):
        if len(dict_1) < len(dict_2):
            dict_long = dict_2
            dict_short = dict_1
        else:
            dict_long = dict_1
            dict_short = dict_2

        combined_dict = dict(dict_long)
        for key in dict_long:
            if key in dict_short:
                for key_second in dict_long[key].keys():
                    combined_dict[key][key_second] = dict_long[key][key_second]
            else:
                del combined_dict[key]
        return combined_dict

    
