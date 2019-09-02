import numpy as np 
from itertools import product
import pickle 


class ColocalisationResult(object):
    def __init__(self, name, channel_name,  n_objects, other_channels):
        self.name = name
        self.channel_name = channel_name
        self.n_objects = n_objects
        self.all_channels = other_channels
        self.all_channels.append(channel_name)
        self.combination_maps = self._get_combination_maps()
        self.result_maps = self._get_result_maps()
        self.results = {x:0 for x in (self.result_maps)}
        self.colocalisations = [{x:(1 if x is channel_name else 0) for x in self.all_channels}
                                for y in range(self.n_objects)]
   

    def get_results(self):
        for coloc in self.colocalisations:
            for result in self.results:
                if self.result_maps[result] == coloc:
                    self.results[result]+=1
        return self.results
        

    def print_colocalisations(self):
        for x in self.colocalisations:
            print(x)


    def save_to_pickle(self, output_dir, output_name=None):
        if output_name:
            file_name = "{0}/{1}_results.pickle".format(output_dir, output_name)
        else:
            file_name = "{0}/{1}_results.pickle".format(output_dir, self.name)

        with open(file_name, "wb") as output_file:
            pickle.dump(self.results, output_file)

        
    def _get_combination_maps(self):
        combination_maps = []
        binary_combinations = [list(i) for i in 
            product([0, 1], repeat=len(self.all_channels)) 
            if i[-1] == 1]
        
        for combination in binary_combinations:
            temp_map = {}
            for i,channel in enumerate(self.all_channels):
                temp_map[channel] = combination[i]
            combination_maps.append(temp_map)

        return combination_maps


    def _get_result_maps(self):
        result_maps = {}
        for combination_map in self.combination_maps:
            result_str = ""
            for key in combination_map:
                if combination_map[key]:
                    result_str+=key
            result_maps[result_str] = combination_map
  
        return result_maps



