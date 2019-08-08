import yaml


def get_syn_config():
    with open("config.yml", "r") as ymlfile:
        return yaml.load(ymlfile)
