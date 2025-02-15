import os
import sys
import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Define the path to the config file
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

config_file = os.path.join(base_path, "config.ini")

# Create the config file if it does not exist
if not os.path.isfile(config_file):
    with open(config_file, 'w') as file:
        config.write(file)

# Read the config file
config.read(config_file)

def get_config(section, option, fallback=None):
    """
    Get a configuration value.
    
    :param section: The section of the config file.
    :param option: The option within the section.
    :param fallback: The fallback value if the option is not found.
    :return: The value of the configuration option.
    """
    if not os.path.isfile(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    return config.get(section, option, fallback=fallback)

def set_config(section, option, value):
    """
    Set a configuration value and save it to the config file.
    
    :param section: The section of the config file.
    :param option: The option within the section.
    :param value: The value to set.
    """
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)
    with open(config_file, 'w') as configfile:
        config.write(configfile)