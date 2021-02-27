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

filetype_content_map = {
    "xml": "application/xml",
    "json": "application/json",
    "jpeg": "image/jpg",
    "jpg": "image/jpg"
}

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
            format="%(asctime)s %(levelname)s %(threadName)s %(message)s"
        )
    logging.debug("Starting SynEx, data delivery tool.")

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    endpoints = (config["global"]["endpoints"].replace(' ', '').split(','))

    handlers = []
    for endpoint in endpoints:
        try:
            courier = Courier(config[endpoint]["url"])
            handlers.append(DestinationHandler(courier, config[endpoint]["dir"], endpoint))
        except KeyError:
            missing_config_section_error(endpoint, args.conf)

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
                handler.join()
            sys.exit(0)

def exit_gracefully(signum, frame):
    """Iterrupt signal handler for graceful shutdown"""
    logging.debug("captured signal %d", signum)

    raise SystemExit


def missing_config_section_error(section_name, conf_file_path):
    """Log error about missing section in configfile."""
    logging.error("Missinf %s section in configfile %s", section_name, conf_file_path)


class DestinationHandler(threading.Thread):
    """Class object creates thread that handles incoming data"""

    def __init__(self, courier, outbox, name, shipment_limit=100):
        self.courier = courier
        self.outbox = outbox
        self.shipment_limit = shipment_limit

        threading.Thread.__init__(self)
        #self.daemon = True
        self.name = name + "_handler"
        self.should_run = True

        if not os.path.isdir(outbox):
            logging.error("Outbox dir %s doen not exist, this handler will not run.")
            self.should_run = False

    def dispatch(self):
        """Check outbox dir for files to send and use courier object to send them."""
        packages = os.listdir(self.outbox)
        self.courier.deliver_packages(packages[:self.shipment_limit], self.outbox)

    def run(self):
        """Thread run method"""
        logging.info("Starting handler thread.")
        while self.should_run:
            self.dispatch()
            time.sleep(15)

    def stop(self):
        """Stops thread infinite loop"""
        self.should_run = False


class Courier():
    """Class used for handling data delivery."""

    def __init__(self, receiver):
        self.receiver = receiver

    def deliver_packages(self, packages, outbox):
        """Use subprocesses to send list of packages"""
        processes = []
        for package in packages:
            process = multiprocessing.Process(target=self.delivery, args=(package, outbox,))
            process.start()
            processes.append(process.sentinel)


    def delivery(self, package, outbox):
        """Send file form outbox dir using http POST, file is deleted if code 200 was returned."""
        logging.debug(
            "Courier will try to deliver %s from outbox %s to %s", package, outbox, self.receiver
        )
        package_filepath = os.path.join(outbox, package)
        parts = package.split("-")
        package_sender_location = parts[0] + "=" + parts[1]

        try:
            file_type = package.split(".")[-1]
            package_content_type = filetype_content_map[file_type]
        except KeyError:
            logging.error("Wrong file type %s", file_type)
            return False

        headers = {
            "file-name": package,
            "content-type": package_content_type,
            "location": package_sender_location
        }
        try:
            with open(package_filepath, "rb") as package_file:
                package_content = package_file.read()
        except IOError:
            logging.error("Error reading file %s", package)
            return False

        try:
            request = requests.post(
                self.receiver, headers=headers, data=package_content, timeout=10
            )
        except requests.RequestException:
            logging.error("Failed to deliver package %s", package)
            return False

        if request.status_code == 200:
            os.remove(package_filepath)
            logging.error("Package %s delivered", package)
        else:
            logging.error(
                "Failed to deliver package %s, response code: %s", package, request.status_code
            )
            return False

        return True


if __name__ == "__main__":
    main()
