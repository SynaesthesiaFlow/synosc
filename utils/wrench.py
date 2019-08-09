import yaml
from os.path import dirname, abspath
import os


def get_syn_config():
    with open(os.path.join(dirname(dirname(abspath(__file__))), "config.yml"), "r") as ymlfile:
        return yaml.load(ymlfile)


def get_abs_fnames_in_dir(directory_name):
    return [os.path.join(directory_name, f) for f in os.listdir(directory_name)]
