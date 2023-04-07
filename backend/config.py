import os
import configparser
import logging
import secrets
from pathlib import Path
from backend.utils import pickle_it

home = Path.home()
# make directory to store all private data at /home/.warden
# /root/.swan_data/
home_dir = os.path.join(home, '.swan_data/')
basedir = os.path.abspath('')

# Check if the home directory exists, if not create it
try:
    os.mkdir(home_dir)
except Exception:
    pass


def load_config():
    # Load Config
    config_file = os.path.join(basedir, 'pricing_engine/APIs.ini')
    CONFIG = configparser.ConfigParser()
    CONFIG.read(config_file)
    return (CONFIG)
