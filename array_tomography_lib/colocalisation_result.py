import pickle
import itertools

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
                pass
                
    def _combine_dicts(self, dict_1, dict_2):
        for key in dict_2:
            if key in dict_1:
                dict_2_key = list(dict_2[key].keys())[0]
                dict_1[key][dict_2_key] = dict_2[key][dict_2_key]
            else:
                dict_1[key] = dict_2[key]
        return dict_1