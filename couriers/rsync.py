#!/bin/python3

import logging
import multiprocessing
import os
import time
import requests
import subprocess

class Courier():
    """Class used for handling data delivery using rsync protocol."""

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


        try:
            request = subprocess.call([
                "/usr/bin/rsync",
                "-q",
                "--remove-source-files",
                "--timeout=10",'-e',
                'ssh', '-o', 'ConnectTimeout=10',
                package_filepath,
                self.receiver
            ])
        except FileNotFoundError:
            logging.error("Failed to deliver package %s, rsync executable missing", package)
            return False

        if request == 0:
            os.remove(package_filepath)
            logging.info("Package %s delivered", package)
        else:
            logging.error(
                "Failed to deliver package %s, rsync error code: %s", package, request
            )
            return False

        return True

