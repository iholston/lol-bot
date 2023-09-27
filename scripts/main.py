"""
Where bot execution starts, sets logging configurations
"""

import logging
import os
import sys
import constants
from client import Client
from datetime import datetime
from logging.handlers import RotatingFileHandler


def set_logs(dir_path: str) -> None:
    """Sets log output to file and console"""
    filename = os.path.join(dir_path, datetime.now().strftime('%d%m%Y_%H%M_log.log'))
    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s', datefmt='%d %b %Y %H:%M:%S')
    logging.getLogger().setLevel(logging.DEBUG)

    fh = RotatingFileHandler(filename=filename, maxBytes=500000, backupCount=1)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logging.getLogger().addHandler(ch)


if __name__ == '__main__':
    if not os.path.exists(constants.LEAGUE_CLIENT_DIR):
        raise ValueError("League Directory is incorrect. Please update the path in constants.py")

    log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    set_logs(dir_path=log_dir)

    client: Client = Client()
    client.account_loop()
