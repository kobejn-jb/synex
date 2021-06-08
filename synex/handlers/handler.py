"""DestinationHandler class should be inherited by all handler classes"""

import logging
import os
import re
import threading
import time


class DestinationHandler(threading.Thread):
    """Class object creates thread that handles incoming data"""

    def __init__(self, courier, config, name):
        self.courier = courier
        self.outbox = config["dir"]
        if "limit" in config:
            self.shipment_limit = config["limit"]
        else:
            self.shipment_limit = 100

        try:
            if "regex" in config:
                self.regex = re.compile(config["regex"])
            else:
                self.regex = None
        except re.error:
            logging.error("Bad format of regex expression %s", config["regex"])
            self.regex = None

        threading.Thread.__init__(self)
        self.name = name + "_handler"
        # self.daemon = True
        self.should_run = True

    def dispatch(self):
        """All handler classes should implement this method to use courier
        object for sending files."""
        logging.info("Running dummy dispatch function, select hendler type in config file to actually sand some files")

    def filter_by_regex(self, in_list):
        """Filters out all file names that does not match regex defined in config"""
        filtered = [i for i in in_list if self.regex.match(i)]
        return filtered

    def run(self):
        """Thread run method"""
        logging.info("Starting handler thread.")

        if not os.path.isdir(self.outbox):
            logging.error("Outbox dir %s does not exist, this handler will not run.", self.outbox)
            self.should_run = False

        while self.should_run:
            self.dispatch()
            time.sleep(15)
        logging.info("Stopping handler thread.")

    def stop(self):
        """Stops thread infinite loop"""
        self.should_run = False
