import glob
import os
import logging

import yaml

from lib import File, segmentation, utils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s:%(levelname)s: %(message)s')

def server_run_segment(config: dict):
    input_dir = config["input_dir"]
    output_dir = config["output_dir"]
    file_pattern = config["files"]
    threshold_method = config["threshold_method"]
    threshold_params = config["threshold_params"]
    utils.check_dir_exists(input_dir)
    utils.check_dir_exists(output_dir)
    _save_config(config)

    files_to_segment = glob.glob(f"{input_dir}/{file_pattern}")
    logger.info(f"{files_to_segment}")
    for i, file_name in enumerate(files_to_segment):
        logger.info(f"{i+1}/{len(files_to_segment)}")
        channel_file = File.from_tiff(file_name)
        segmented_file = segmentation.segment_stack(channel_file, threshold_method, 3, 90000, **threshold_params)
        segmented_file.save_to_tiff(output_dir)

def _save_config(config):
    with open(os.path.join(config["output_dir"], "config.yml"), "w") as config_file:
        yaml.dump(config, config_file)
