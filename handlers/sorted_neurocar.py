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
import re
import datetime
#import inotify.adapters

def remove_duplicates(list_in):

    return list(set(list_in))


class DestinationHandler(threading.Thread):
    """Class object creates thread that handles incoming data"""

    def __init__(self, courier, outbox, name, shipment_limit=100):
        self.courier = courier
        self.outbox = outbox
        self.shipment_limit = shipment_limit
        #self.inotify_adapter = inotify.adapters.Inotify()

        threading.Thread.__init__(self)
        #self.daemon = True
        self.name = name + "_handler"
        self.should_run = True


    def sort_input(self):

        packages = os.listdir(self.outbox)

        ids = []

        for package in packages:
            pass_id = re.findall("[0-9]{8}-[0-9]{6}-[0-9]{3}", package)
            if pass_id:
                ids.append(pass_id[0])

        ids = remove_duplicates(ids)
        ids.sort()

        for pass_id in ids:
            now = datetime.datetime.utcnow() - datetime.timedelta(seconds = 10)
            id_limit = datetime.datetime.strftime(now, "%Y%m%d-%H%M%S-%f")
            files_to_send = []
            if pass_id > id_limit:
                return
            for package in packages:
                if re.findall(pass_id, package):
                    files_to_send.append(package)
            self.dispatch(files_to_send)


    def dispatch(self, packages):
        """Check outbox dir for files to send and use courier object to send them."""

        self.courier.deliver_packages(packages[:self.shipment_limit], self.outbox)

    def run(self):
        """Thread run method"""
        logging.info("Starting handler thread.")

        if not os.path.isdir(self.outbox):
            logging.error("Outbox dir %s doen not exist, this handler will not run.", self.outbox)
            return

        #self.inotify_adapter.add_watch(self.outbox)

        while self.should_run:
            #self.dispatch()
            self.sort_input()
            time.sleep(15)
        logging.info("Stopping handler thread.")

    def stop(self):
        """Stops thread infinite loop"""
        self.should_run = False
