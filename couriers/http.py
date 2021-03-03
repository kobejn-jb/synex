#!/bin/python3

import logging
import multiprocessing
import os
import time
import requests

filetype_content_map = {
    "xml": "application/xml",
    "json": "application/json",
    "jpeg": "image/jpg",
    "jpg": "image/jpg"
}

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

        try:
            file_type = package.split(".")[-1]
            package_content_type = filetype_content_map[file_type]
        except KeyError:
            logging.error("Wrong file type %s", file_type)
            return False

        headers = {
            "file-name": package,
            "content-type": package_content_type
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
            logging.info("Package %s delivered", package)
        else:
            logging.error(
                "Failed to deliver package %s, response code: %s", package, request.status_code
            )
            return False

        return True

