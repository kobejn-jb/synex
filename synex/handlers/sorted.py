"""Handler class used for sending files form selected directory using designated courier object,
it send number of files limited by shipment_limit form top of files list sorted by name"""

import os
from .handler import DestinationHandler


class SortedHandler(DestinationHandler):
    """Class object creates thread that handles incoming data"""

    def dispatch(self):
        """Check outbox dir for files to send and use courier object to send them."""
        packages = os.listdir(self.outbox)
        if self.regex:
            packages = self.filter_by_regex(packages)
        packages.sort()
        self.courier.deliver_packages(packages[: self.shipment_limit], self.outbox)
