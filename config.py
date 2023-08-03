import os

from dotenv import load_dotenv
import yaml

load_dotenv()

local_config = {}

try:
    with open(os.getenv('CONFIG_FILE'), 'r') as f:
        local_config = yaml.safe_load(f)
except FileNotFoundError:
    pass

def get(option, default=None):
    return local_config.get(option, default)


def set(option, value):
    local_config[option] = value
    with open(os.getenv('CONFIG_FILE'), 'w') as f:
        yaml.safe_dump(local_config, f)
