import os

import numpy as np
import yaml
from numba import njit

from lib import logger


def check_dir_exists(dir):
    if not os.path.isdir(dir):
        logger.error(f"{dir} does not exist. Check your paths are all correct!")
        exit()

def parse_config(config_path: str) -> dict:
    try:
        with open(config_path) as f:
            config_dict = yaml.load(f, Loader=yaml.Loader)
        return config_dict
    except FileNotFoundError:
        logger.log(level="error", message="Config file does not exist! Check the path/name are correct.")
        exit()

@njit(cache=True, fastmath=True)
def set_pixels(image: np.array, coords: np.ndarray, value: int) -> None:
    """Function to set the pixel values for a given set of coordinates"""
    if len(coords.shape) == 1:
        _maybe_2D_pixel(image, coords, value)
    else:
        for i in range(len(coords)):
            pixel = coords[i]
            _maybe_2D_pixel(image, pixel, value)

@njit(cache=True, fastmath=True)
def _maybe_2D_pixel(image: np.array, pixel: np.ndarray, value: int) -> None:
    """Change how pixel values are set if the image is only 2D"""
    if len(pixel) == 2:
        image[pixel[0]][pixel[1]] = value
    elif len(pixel) == 3:
        image[pixel[0]][pixel[1]][pixel[2]] = value
