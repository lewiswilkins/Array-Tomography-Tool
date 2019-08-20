from numba import njit
from math import sqrt
from ColocalisationResult import ColocalisationResult


class Colocalisation(object):
    def __init__(self, channels_arr=None, xy_resolution=0.102, z_resolution=0.07,
                max_distance=0.5, min_overlap=0.1):
        if channels_arr:
            self.channels_arr = channels_arr
            self.channel_names = [channel.name for channel in channels_arr]
            self.results_arr = [ColocalisationSave(self.channels_arr[i].name, 
                                                   len(elf.channels_arr[i]).centroids),
                                                    [names for names in self.channel_names
                                                    if names not self.channels_arr[i].name])
                                                    for i in range(len(channels_arr))]
        self.xy_resolution = xy_resolution
        self.z_resolution = z_resolution
        self.max_distance = max_distance
        self.min_overlap = min_overlap
        
        
    def set_channels_arr(self, channels_arr):
        self.channels_arr = channels_arr
    
    
    def fill_distance_jit(channels):
        for channel_i in self.channels_arr:
            print("Comparing {0} with all other channels.".format(channel_i.name))
            for centroid_i in channels_i.centroids:
                for channel_j in self.channels_arr:
                    centroids_j = channel_j.centroids
                    distance = self._get_best_distance(centroid_i, centroids_j)
                    if distance < 0.5:
                        channels[channel_i]["distance"] = distance
            end = time.time()
            print("time = {0}s, iterations = {1}".format(end-start, iterations))


    @njit(cache=True, fastmath=True)
    def _get_best_distance(centroids, centroids_list, xy_resolution=0.102,
                            z_resolution=0.07):
        best_distance = 9999
        for i in range(centroids_j.shape[0]):
            distance = sqrt(pow((centroids[0]-centroids_list[i][0])*xy_resolution,2)+
                            pow((centroids[1]-centroids_list[i][1])*xy_resolution,2)+
                            pow((centroids[2]-centroids_list[i][2])*z_resolution,2))
            
            if distance < best_distance:
                best_distance = distance
        return best_distance