"""
Handles HTTP Requests for Riot Client and League Client
"""

import logging
from base64 import b64encode
from time import sleep

import requests
import urllib3

import lolbot.common.config as config


class Connection:
    """Handles HTTP requests for Riot Client and League Client"""

    LCU_HOST = '127.0.0.1'
    RCU_HOST = '127.0.0.1'
    LCU_USERNAME = 'riot'
    RCU_USERNAME = 'riot'

    def __init__(self) -> None:
        self.client_type = ''
        self.client_username = ''
        self.client_password = ''
        self.procname = ''
        self.pid = ''
        self.host = ''
        self.port = ''
        self.protocol = ''
        self.headers = ''
        self.session = requests.session()
        self.config = config.ConfigRW()
        self.log = logging.getLogger(__name__)
        logging.getLogger('urllib3').setLevel(logging.INFO)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def set_rc_headers(self) -> None:
        """Sets header info for Riot Client"""
        self.log.debug("Initializing Riot Client session")
        self.host = Connection.RCU_HOST
        self.client_username = Connection.RCU_USERNAME

        # lockfile
        lockfile = open(config.Constants.RIOT_LOCKFILE, 'r')
        data = lockfile.read()
        self.log.debug(data)
        lockfile.close()
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass), "Content-Type": "application/json"}
        self.log.debug(self.headers['Authorization'])

    def set_lcu_headers(self, verbose: bool = True) -> None:
        """Sets header info for League Client"""
        self.host = Connection.LCU_HOST
        self.client_username = Connection.LCU_USERNAME

        # lockfile
        lockfile = open(self.config.get_data('league_lockfile'), 'r')
        data = lockfile.read()
        self.log.debug(data)
        lockfile.close()
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass)}
        self.log.debug(self.headers['Authorization'])

    def connect_lcu(self, verbose: bool = True) -> None:
        """Tries to connect to league client"""
        if verbose:
            self.log.info("Connecting to LCU API")
        else:
            self.log.debug("Connecting to LCU API")
        self.host = Connection.LCU_HOST
        self.client_username = Connection.LCU_USERNAME

        # lockfile
        lockfile = open(self.config.get_data('league_lockfile'), 'r')
        data = lockfile.read()
        self.log.debug(data)
        lockfile.close()
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass)}
        self.log.debug(self.headers['Authorization'])

        # connect
        for i in range(30):
            sleep(1)
            try:
                r = self.request('get', '/lol-login/v1/session')
            except:
                continue
            if r.json()['state'] == 'SUCCEEDED':
                if verbose:
                    self.log.info("Connection Successful")
                else:
                    self.log.debug("Connection Successful")
                self.request('post', '/lol-login/v1/delete-rso-on-close')  # ensures self.logout after close
                sleep(2)
                return
        raise Exception("Could not connect to League Client")

    def request(self, method: str, path: str, query: str = '', data: dict = None) -> requests.models.Response:
        """Handles HTTP requests to Riot Client or League Client server"""
        if data is None:
            data = {}
        if not query:
            url = "{}://{}:{}{}".format(self.protocol, self.host, self.port, path)
        else:
            url = "{}://{}:{}{}?{}".format(self.protocol, self.host, self.port, path, query)

        if 'username' not in data:
            self.log.debug("{} {} {}".format(method.upper(), url, data))
        else:
            self.log.debug("{} {}".format(method.upper(), url))

        fn = getattr(self.session, method)

        if not data:
            r = fn(url, verify=False, headers=self.headers)
        else:
            r = fn(url, verify=False, headers=self.headers, json=data)
        return r
