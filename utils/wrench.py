import yaml
from os.path import dirname, abspath
import os


def get_syn_config():
    with open(os.path.join(dirname(dirname(abspath(__file__))), "config.yml"), "r") as ymlfile:
        return yaml.load(ymlfile)
