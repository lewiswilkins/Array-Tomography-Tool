import pickle
from itertools import product

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
    
    def _calculate_combinations(self):
        for combination in product(self.colocalised_images):
            image_1 = combination[0]
            image_2 = combination[1]

            image_1_coords = image_1.object_coords
            image_2_coords = image_2.object_coords
            colocalised_image = np.copy(image_1.image)
            colocalised_image.fill(0)
            for label in image_1.object_list:
                if label in image_2.object_list:
                    colocalised_image = self._fill_image(colocalised_image, image_1_coords)
                    

    def _fill_image(self, image, coords):
        for coord in coords:
            image[coord[0]][coord[1]][coord[2]] = 1
        return image 
        


        #this should be a function which calculates the additional images where
        #the original channel is colocalised with more than a single channel
        
        pass

# class ColocalisationResult:
#     """The colocalisations for one image stack. Contains a list of all colocalisation
#     possibilities for every subset of channels"""

#     def __init__(self, case_stack, channel_name, n_objects, other_channels):
#         self.case_stack = case_stack
#         self.channel_name = channel_name
#         self.n_objects = n_objects
#         self.all_channels = other_channels
#         self.all_channels.append(channel_name)
#         self.combination_maps = self._get_combination_maps()
#         self.result_maps = self._get_result_maps()
#         self.results = {x: 0 for x in (self.result_maps)}
#         self.colocalisations = [
#             {x: (1 if x is channel_name else 0) for x in self.all_channels}
#             for y in range(self.n_objects)
#         ]

#     def get_results(self):
#         for coloc in self.colocalisations:
#             for result in self.results:
#                 if self.result_maps[result] == coloc:
#                     self.results[result] += 1
#         return self.results

#     def print_colocalisations(self):
#         for x in self.colocalisations:
#             print(x)

#     def save_to_pickle(self, output_dir, output_name=None):
#         if output_name:
#             file_name = f"{output_dir}/{output_name}_results.pickle"
#         else:
#             file_name = f"{output_dir}/{self.name}_results.pickle"

#         with open(file_name, "wb") as output_file:
#             pickle.dump(self.results, output_file)

#     def _get_combination_maps(self):
#         combination_maps = []
#         binary_combinations = [
#             list(i) for i in product([0, 1], repeat=len(self.all_channels)) if i[-1] == 1
#         ]

#         for combination in binary_combinations:
#             temp_map = {}
#             for i, channel in enumerate(self.all_channels):
#                 temp_map[channel] = combination[i]
#             combination_maps.append(temp_map)

#         return combination_maps

#     def _get_result_maps(self):
#         result_maps = {}
#         for combination_map in self.combination_maps:
#             result_str = ""
#             for key in combination_map:
#                 if combination_map[key]:
#                     result_str += key
#             result_maps[result_str] = combination_map

#         return result_maps
