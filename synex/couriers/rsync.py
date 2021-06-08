"""Rsync courier module"""

import logging
import os
import subprocess
from .courier import Courier


class CourierRsync(Courier):
    """Class used for handling data delivery using rsync protocol."""

    def delivery(self, package, outbox):
        """Send file form outbox dir using rsync, file is deleted affter being sent."""
        logging.debug("Courier will try to deliver %s from outbox %s to %s", package, outbox, self.receiver)
        package_filepath = os.path.join(outbox, package)

        rsync_call = [
            "/usr/bin/rsync",
            "-q",
            "--remove-source-files",
            "--timeout=10",
            #'-e', 'ssh', '-o', 'ConnectTimeout=10',
            package_filepath,
            self.receiver,
        ]

        try:
            request = subprocess.call(rsync_call)
        except FileNotFoundError:
            logging.error("Failed to deliver package %s, rsync executable missing", package)
            return False

        if request == 0:
            # os.remove(package_filepath)
            logging.info("Package %s delivered", package)
        else:
            logging.error("Failed to deliver package %s, rsync error code: %s", package, request)
            return False

        return True
