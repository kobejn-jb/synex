"""Base courier module"""

import logging
import multiprocessing


class Courier:
    """Base class used for handling data delivery, other courier classes shoudl inherit from this class"""

    def __init__(self, receiver):
        self.receiver = receiver
        self.timeout = 10

    def deliver_packages(self, packages, outbox):
        """Use subprocesses to send list of packages"""
        processes = []
        for package in packages:
            process = multiprocessing.Process(target=self.delivery, args=(package, outbox))
            process.start()
            # processes.append(process.sentinel)
            processes.append(process)
        return processes

    def delivery(self, package, outbox):
        """All courier classes should implement this method to send files and delete them in outbox dir"""
        logging.debug("Courier will try to deliver %s from outbox %s to %s", package, outbox, self.receiver)
        return True
