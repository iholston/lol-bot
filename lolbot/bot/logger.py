"""
Sets global logging state.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from multiprocessing import Queue

import lolbot.common.config as config


class MultiProcessLogHandler(logging.Handler):
    """Sets log configuration and pushes logs onto message queue for display in view"""

    def __init__(self, message_queue: Queue) -> None:
        logging.Handler.__init__(self)
        self.message_queue = message_queue

    def emit(self, record: logging.LogRecord) -> None:
        """Adds log to message queue"""
        msg = self.format(record)
        self.message_queue.put(msg)

    def set_logs(self) -> None:
        """Sets log configurations"""
        if not os.path.exists(config.LOG_DIR):
            os.makedirs(config.LOG_DIR)

        filename = os.path.join(config.LOG_DIR, datetime.now().strftime('%d%m%Y_%H%M.log'))
        formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s',datefmt='%d %b %Y %H:%M:%S')
        logging.getLogger().setLevel(logging.INFO)

        fh = RotatingFileHandler(filename=filename, maxBytes=1000000, backupCount=1)
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        logging.getLogger().addHandler(fh)

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        ch.setLevel(logging.INFO)
        logging.getLogger().addHandler(ch)

        self.setFormatter(logging.Formatter(fmt='[%(asctime)s] [%(levelname)-7s] %(message)s', datefmt='%H:%M:%S'))
        self.setLevel(logging.INFO)
        logging.getLogger().addHandler(self)
