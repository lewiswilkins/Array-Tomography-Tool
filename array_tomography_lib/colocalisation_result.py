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
        channel_name: str,
        original_objects=None
    ):
        self.case_number = case_number
        self.stack_number = stack_number
        self.channel_name = channel_name
        self.colocalised_images = []
        self.original_objects = original_objects
    
    @classmethod
    def from_channel_file(cls, channel_file):
        return cls(
            case_number=channel_file.case_number,
            stack_number=channel_file.stack_number,
            channel_name=channel_file.channel_name,
            original_objects=channel_file.objects
        )

    def add_colocalised_image(self, colocalised_image: ColocalisedChannelFile):
        self.colocalised_images.append(colocalised_image)
        print(f"There are {len(self.colocalised_images)} in the object.")
    
    def calculate_combination_images(self):
        for x in range(2, len(self.colocalised_images) + 1):
            for combination in itertools.combinations(self.colocalised_images, x):
                object_lists = (image.object_list for image in combination)
                combined_object_list = functools.reduce(self._combine_dicts, object_lists)
                temp_colocalised_channel_file = ColocalisedChannelFile(
                    image=None,
                    case_number=self.case_number,
                    stack_number=self.stack_number,
                    channel_name=self.channel_name,
                    colocalised_with=self._get_colocalised_with_string(combination),
                    object_list=combined_object_list
                )
            self.colocalised_images.append(temp_colocalised_channel_file)
    
    def _get_colocalised_with_string(self, images):
        colocalised_with_string = ""
        for image in images:
            colocalised_with_string += image.colocalised_with 
        return colocalised_with_string

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