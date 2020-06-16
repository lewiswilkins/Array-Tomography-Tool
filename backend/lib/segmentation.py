import logging

import numpy as np
from matplotlib.pyplot import figure
from skimage.filters import threshold_local
from skimage import io

from lib import File, SegmentedFile, ATLogger, utils

logger = ATLogger(__name__)


def segment_stack(
    channel_file: File, threshold_method: str, min_vox_size: int = 3, 
    max_vox_size: int = 9999999, **params: int
) -> SegmentedFile:
    """Applies a thresholding method to an image stack and returns the segmented image stack.
        Args:
            channel_file: The `File` object containing the image stack to segment
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
            logger.log(
                level="error", 
                message=f"{threshold_method} is not a valid method! Please use another."
                )
        segmented_image = threshold_function(image=image, **params)
        segmented_stack.append(segmented_image)

    segmented_image = SegmentedFile(
        np.array(segmented_stack), channel_file.name, channel_file.channel_name
        )
    
    for obj in segmented_image.objects:
        if obj.area < min_vox_size or obj.area > max_vox_size:
            coords = obj.coords
            utils.set_pixels(segmented_image.image, coords, 0)
    
    return segmented_image 
            

def autolocal_threshold(image, window_size, c_factor, method="mean", show_image=False):
    C =-image.mean()/c_factor
    threshold = threshold_local(
        image, block_size=int(window_size), offset=C, method=method
        )
    threshold_image = (image > threshold)*1
    if show_image:
        figure(figsize=(10,20))
        io.imshow(threshold_image)
    return threshold_image


def fixed_threshold(image, threshold):
    threshold_image = (image > threshold)*1
    return threshold_image


segment_methods = {
        "autolocal": autolocal_threshold,
        "fixed": fixed_threshold,
    }