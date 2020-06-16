#!/usr/bin/env python
import json
import sys

from modules import segment


def cast_config(config, keys):
    for key in keys:
        if key in config:
            config[key] = float(config[key])


if __name__ == "__main__":
    print("Im running ")
    config_string = sys.argv[1].replace("'", '"')
    config = json.loads(config_string)
    cast_config(config["threshold_params"], ["threshold", "c_factor", "window_size"])
    print((config))
    segment.server_run_segment(config)
