import logging
import os
import sys
import constants
from client import Client
from datetime import datetime
from logging.handlers import RotatingFileHandler

def set_logs(log_dir, level=logging.INFO) -> None:
    """Sets log output to file and console"""
    filename = os.path.join(log_dir, datetime.now().strftime('%d%m%Y_%H%M_log.log'))

    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s',
                                  datefmt='%d %b %Y %H:%M:%S')

    ch = logging.StreamHandler(sys.stdout)
    fh = RotatingFileHandler(filename=filename, maxBytes=500000, backupCount=1)

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logging.getLogger().addHandler(ch)
    logging.getLogger().addHandler(fh)

    logging.getLogger().setLevel(level)

if __name__ == '__main__':
    if not os.path.exists(constants.LEAGUE_CLIENT_DIR):
        raise ValueError("League Directory is incorrect. Please update the path in constants.py")

    log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    set_logs(log_dir=log_dir)

    client: Client = Client()
    client.main_loop()
