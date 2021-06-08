"""HTTP courier module"""

import logging
import os
import requests
from .courier import Courier

filetype_content_map = {
    "xml": "application/xml",
    "json": "application/json",
    "jpeg": "image/jpg",
    "jpg": "image/jpg",
    "gif": "image/gif",
    "png": "image/png",
    "tiff": "image/tiff",
}


class CourierHttp(Courier):
    """Class used for handling data delivery using http protocol."""

    def delivery(self, package, outbox):
        """Send file form outbox dir using http POST, file is deleted if code 200 was returned."""
        logging.debug("Courier will try to deliver %s from outbox %s to %s", package, outbox, self.receiver)
        package_filepath = os.path.join(outbox, package)

        headers = {"file-name": package}

        try:
            file_type = package.split(".")[-1]
            package_content_type = filetype_content_map[file_type]
            headers["content-type"] = package_content_type
        except KeyError:
            logging.info("File type %s won't be put in content-type header", file_type)
        except IndexError:
            logging.info("Unknown content-type won't be put in headers")

        try:
            with open(package_filepath, "rb") as package_file:
                package_content = package_file.read()
        except IOError:
            logging.error("Error reading file %s", package)
            return False

        try:
            request = requests.post(self.receiver, headers=headers, data=package_content, timeout=self.timeout)
        except requests.RequestException:
            logging.error("Failed to deliver package %s", package)
            return False

        if request.status_code == 200:
            os.remove(package_filepath)
            logging.info("Package %s delivered", package)
        else:
            logging.error("Failed to deliver package %s, response code: %s", package, request.status_code)
            return False

        return True
