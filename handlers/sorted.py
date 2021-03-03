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

    def dispatch(self):
        """Check outbox dir for files to send and use courier object to send them."""
        packages = os.listdir(self.outbox)
        self.courier.deliver_packages(packages[:self.shipment_limit], self.outbox)

    def run(self):
        """Thread run method"""
        logging.info("Starting handler thread.")

        if not os.path.isdir(self.outbox):
            logging.error("Outbox dir %s doen not exist, this handler will not run.", self.outbox)
            self.should_run = False

        while self.should_run:
            self.dispatch()
            time.sleep(15)
        logging.info("Stopping handler thread.")

    def stop(self):
        """Stops thread infinite loop"""
        self.should_run = False
