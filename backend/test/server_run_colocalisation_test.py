#!/usr/bin/env python

import json
import sys

from array_tomography_tool import server_run_colocalisation


def cast_config(config, keys):
    for key in keys:
        config[key] = float(config[key])


if __name__ == "__main__":
    config_string = sys.argv[1].replace("'", '"')
    config = json.loads(config_string)
    cast_config(config, ["xy_resolution", "z_resolution", "min_overlap", "max_distance"])

    server_run_colocalisation(config)
