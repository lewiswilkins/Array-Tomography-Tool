import numpy as np
from skimage import exposure

from lib import File


def rescale_intensity(channel_file: File, lower_percentile=2, upper_percentile=98) -> np.ndarray:
    image_stack = channel_file.image
    rescaled_image_stack =[]
    for image in image_stack:
        lower, upper = np.percentile(image, (lower_percentile, upper_percentile))
        rescaled_image = exposure.rescale_intensity(image, in_range=(lower, upper))
        rescaled_image_stack.append(rescaled_image)
    return np.array(rescaled_image_stack)
