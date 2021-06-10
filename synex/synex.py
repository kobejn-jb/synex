#!/bin/python3

import argparse
import configparser
import logging
import multiprocessing
import os
import sys
import signal
import threading
import time
import requests


class CourierError(Exception):
    pass


class HandlerError(Exception):
    pass


def main():
    """Main function"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', type=str, help='path to config file')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.conf)
    if "global" not in config:
        missing_config_section_error("global", args.conf)
        sys.exit(1)

    if "logfile" in config["global"]:
        logging.basicConfig(
            filename=config["global"]["logfile"],
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(threadName)s %(message)s",
        )
    else:
        logging.basicConfig(
            stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(message)s"
        )
    logging.debug("Starting SynEx, data delivery tool.")

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    if "destinations" not in config["global"]:
        missing_config_key_error("destionations", "global", args.conf)
        sys.exit(1)

    destinations = config["global"]["destinations"].replace(' ', '').split(',')

    handlers = []
    for destination in destinations:
        try:
            courier = get_courier(config[destination])
            handlers.append(get_handler(config[destination], destination, courier))
        except KeyError:
            missing_config_section_error(destination, args.conf)
        except CourierError:
            logging.error("Could not start delivery for destination %s, check your config", destination)

    for handler in handlers:
        handler.start()

    while True:
        try:
            time.sleep(10)
        except (KeyboardInterrupt, SystemExit) as exception:
            logging.debug(exception)
            logging.info("Stopping threads, closing program")
            for handler in handlers:
                handler.stop()
            for handler in handlers:
                handler.join()
            sys.exit(0)


def exit_gracefully(signum, frame):
    """Iterrupt signal handler for graceful shutdown."""
    logging.debug("Captured signal %d, will shutdown gracefully", signum)

    raise SystemExit


def missing_config_section_error(section_name, conf_file_path):
    """Log error about missing section in configfile."""
    logging.error("Missing %s section in configfile %s", section_name, conf_file_path)


def missing_config_key_error(key_name, section_name, conf_file_path):
    """Log error about missing key in section in configfile."""
    logging.error("Missing %s in %s section in configfile %s", key_name, section_name, conf_file_path)


def get_courier(destination_config):
    """Returns courier object created acording to destination config."""
    try:
        courier_type = destination_config["protocol"]
        endpoint = destination_config["endpoint"]
    except KeyError:
        logging.error("Missing keys in destionation configuration")
        raise CourierError

    try:
        if courier_type == "http":
            from couriers.http import CourierHttp as Courier
        elif courier_type == "rsync":
            from couriers.rsync import CourierRsync as Courier
        else:
            logging.error("Protocol %s is not supported for delivery", courier_type)
            raise CourierError
    except ImportError:
        logging.error("Failed to import %s courier module", courier_type)
        raise CourierError

    return Courier(endpoint)


def get_handler(destination_config, destination, courier):
    """Returns destination handler according to destination config."""
    try:
        inbox_dir = destination_config["dir"]
        handler_type = destination_config["input_handler"]
    except KeyError:
        logging.error("Missing keys in destionation configuration")
        raise CourierError

    try:
        if handler_type == "sorted":
            from handlers.sorted import SortedHandler as Handler
        else:
            from handlers.handler import DestinationHandler as Handler
    except ImportError:
        logging.error("Failed to import %s handler module", handler_type)
        raise HandlerError

    return Handler(courier, destination_config, destination)


if __name__ == "__main__":
    main()
