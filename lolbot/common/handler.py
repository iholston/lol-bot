"""
Handles bot logging
"""

import logging
import os
import sys
from datetime import datetime
from multiprocessing import Queue

from logging.handlers import RotatingFileHandler


class MultiProcessLogHandler(logging.Handler):
    """Class that handles bot log messsages, writes to log file, terminal, and view"""

    def __init__(self, message_queue: Queue, path: str) -> None:
        logging.Handler.__init__(self)
        self.log_dir = path
        self.message_queue = message_queue

    def emit(self, record: logging.LogRecord) -> None:
        """Adds log to message queue"""
        msg = self.format(record)
        self.message_queue.put(msg)

    def set_logs(self) -> None:
        """Sets log configurations"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        filename = os.path.join(self.log_dir, datetime.now().strftime('%d%m%Y_%H%M.log'))
        formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s',datefmt='%d %b %Y %H:%M:%S')
        logging.getLogger().setLevel(logging.DEBUG)

        fh = RotatingFileHandler(filename=filename, maxBytes=1000000, backupCount=1)
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(fh)

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        ch.setLevel(logging.INFO)
        logging.getLogger().addHandler(ch)

        self.setFormatter(logging.Formatter(fmt='[%(asctime)s] [%(levelname)-7s] %(message)s', datefmt='%H:%M:%S'))
        self.setLevel(logging.INFO)
        logging.getLogger().addHandler(self)
