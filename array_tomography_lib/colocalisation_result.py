import pickle
import itertools
import functools
import numpy as np

from array_tomography_lib import ColocalisedChannelFile


class ColocalisationResult:
    """The colocalisations for one image stack. Contains a list of all colocalisation
     possibilities for every subset of channels"""
    
    def __init__(
        self,
        case_number: str,
        stack_number: str, 
        channel_name: str
    ):
        self.case_number = case_number
        self.stack_number = stack_number
        self.channel_name = channel_name
        self.colocalised_images = []
    
    @classmethod
    def from_channel_file(cls, channel_file):
        return cls(
            case_number=channel_file.case_number,
            stack_number=channel_file.stack_number,
            channel_name=channel_file.channel_name
        )

    def add_colocalised_image(self, colocalised_image: ColocalisedChannelFile):
        self.colocalised_images.append(colocalised_image)
        print(f"There are {len(self.colocalised_images)} in the object.")
    
    def calculate_combination_images(self):
        for x in range(2, len(self.colocalised_images) + 1):
            for combination in itertools.combinations(self.colocalised_images, x):
                object_lists = (image.object_lists for image in combination)
                combined_object_list = functools.reduce(self._combine_dicts, object_lists)
                combined_image = 
                temp_colocalised_channel_file = ColocalisedChannelFile()
    
    def _combine_dicts(self, dict_1, dict_2):
        combined_dict = dict(dict_1)
        for key in dict_2:
            if key in dict_1:
                for key_second in dict_2[key].keys():
                    combined_dict[key][key_second] = dict_2[key][key_second]
            else:
                combined_dict[key] = dict_2[key]
        return combined_dict

    def _combine_images(self, channel_files):
        pass