#!/usr/bin/env python3
import logging
import sys
import os
import traceback
from configparser import ConfigParser

from enoceanmqtt.communicator import Communicator


def load_config_file():
    conf = ConfigParser(inline_comment_prefixes=('#', ';'))
    if len(sys.argv) > 1:
        conf_file = sys.argv[1]
    else:
        conf_file = "/etc/enoceanmqtt.conf"
    if not conf.read(conf_file):
        logging.error("Cannot read config file: {}".format(conf_file))
        sys.exit(1)

    # extract sensor configuration
    sensors = []
    for section in conf.sections():
        # omit special CONFIG section
        if section != 'CONFIG':
            new_sens = {'name': conf['CONFIG']['mqtt_prefix'] + section}
            for key in conf[section]:
                try:
                    new_sens[key] = int(conf[section][key], 0)
                except KeyError:
                    new_sens[key] = None
            sensors.append(new_sens)
    # general configuration is part of CONFIG section
    return sensors, conf['CONFIG']


def setup_logging():
    # set root logger to highest log level
    logging.getLogger().setLevel(logging.DEBUG)

    # create file and console handler
    log_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'enoceanmqtt.log')
    log_file = logging.FileHandler(log_filename)
    log_file.setLevel(logging.INFO)
    log_console = logging.StreamHandler()
    log_console.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    log_file.setFormatter(formatter)
    log_console.setFormatter(formatter)

    # add the handlers to the logger
    logging.getLogger().addHandler(log_file)
    logging.getLogger().addHandler(log_console)


def main():
    """entry point if called as an executable"""
    # setup logger
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    setup_logging()
    
    # load config file
    sensors, conf = load_config_file()

    # start working
    com = Communicator(conf, sensors)
    try:
        com.run()
    # catch all possible exceptions
    except Exception:     # pylint: disable=broad-except
        logging.error(traceback.format_exc())


# check for execution
if __name__ == "__main__":
    main()
