#!/bin/python

import argparse
import glob
import os
import re
import time
import itertools
import multiprocessing
from pandas import DataFrame, read_csv
import gc 
from pathlib import Path
import logging


import yaml

from array_tomography_lib import ChannelFile, colocalisation, ColocalisationResult, segment


CACHE_DIR = ".file_cache"

logger = logging.getLogger(__name__)


def log(config: dict, log_file: str, value):
    """Wirite the frontend logs."""
    if "job_id" in config:
        job_id = config["job_id"]
        if not Path(f"/tmp/{job_id}").exists():
            Path(f"/tmp/{job_id}").mkdir()
        Path(f"/tmp/{job_id}/{log_file}.out").write_text(value)
















def _make_shallow_dict(config_dict):
    """Converts the two-level deep config into a dict"""
    shallow_dict = {}
    for k1, subdict in config_dict.items():
        for k2, v in subdict.items():
            shallow_dict[tuple(sorted((k1, k2)))] = v
    return shallow_dict


def _mkdir_if_not_exists(dir_path):
    if not os.path.isdir(dir_path):
        print("Directory does not exist. Creating now!")
        os.mkdir(dir_path)


def _load_colocalisation_types(file_path):
    with open(file_path) as config_file:
        return yaml.load(config_file)


if __name__ == "__main__":
    main()
