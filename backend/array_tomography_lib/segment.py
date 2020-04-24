import logging

import numpy as np
from matplotlib.pyplot import figure
from skimage import io, exposure
from skimage.filters import threshold_local

from array_tomography_lib import ChannelFile

logger = logging.getLogger(__name__)





def threshold_stack(channel_file: ChannelFile, threshold_method: str, **params):
    """Applies a thresholding method to an image stack and returns the segmented image stack.
        Args:
            channel_file: The `ChannelFile` containing the image stack to segment
            threshold_method: A `str` with the name of the threshold method
            **params: The parameters required for the given threshold method.
            See the threshold method function for the parameters required.
        Returns: A `List` containing the segmented image stack."""
    segment_methods = {
        "autolocal": autolocal_threshold,
        "fixed": fixed_threshold,
    }
    image_stack = channel_file.image
    segmented_stack = []

    for image in image_stack:
        threshold_function = segment_methods.get(threshold_method, None)
        if not threshold_function:
            logger.error(f"{threshold_method} is not a valid method! Please use another.")
        segmented_image = threshold_function(image=image, **params)
        segmented_stack.append(segmented_image)

    return segmented_stack 
            

def autolocal_threshold(image, window_size, c, method="mean", show_image=False):
    C =-image.mean()/c
    threshold = threshold_local(image, block_size=window_size, offset=C, method=method)
    threshold_image = (image > threshold)*1
    
    if show_image:
        figure(figsize=(10,20))
        io.imshow(threshold_image)
    
    return threshold_image


def fixed_threshold(image, threshold):
    threshold_image = (image > threshold)*1

    return threshold_image


def rescale_intensity(channel_file: ChannelFile, lower_percentile=2, upper_percentile=98):
    image_stack = channel_file.image
    rescaled_image_stack =[]
    for image in image_stack:
        lower, upper = np.percentile(image, (lower_percentile, upper_percentile))
        rescaled_image = exposure.rescale_intensity(image, in_range=(lower, upper))
        rescaled_image_stack.append(rescaled_image)
    
    return rescaled_image_stack


segment_methods = {
        "autolocal": autolocal_threshold,
        "fixed": fixed_threshold,
    }