# run with `python -m pytest test/` from the project root directory

import pytest
import yaml

import array_tomography_lib as atl


@pytest.fixture
def raw_config():
    with open("test_data/colocalisation_types.yaml") as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)
    return config_dict


def test_raw_config(raw_config):
    assert raw_config["PSD"]["ALZ50"] == "overlap"
    assert raw_config["PSD"]["ALZ50"] == raw_config["ALZ50"]["PSD"]
