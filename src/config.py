import os
import configparser
from typing import Tuple
from src.error_handler import add_error

def read_config(config_path: str) -> Tuple[str, int, str, str]:
    """
    Reads the configuration values from the config.ini file and returns them as a tuple.
    Expects the following sections and keys in the config.ini file:
    [Main]
    - profiles_dir (str)
    - num_profiles (int)
    - URL (str)
    - start_time (str)
    """
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        profiles_dir = config.get("Main", "profiles_dir")
        num_profiles = config.getint("Main", "num_profiles")
        URL = config.get("Main", "URL")
        start_time = config.get("Main", "start_time")

        return profiles_dir, num_profiles, URL, start_time

    except Exception as e:
        add_error("read_config", str(e))
        return None

if __name__ == "__main__":
    print(read_config("../config.ini"))
