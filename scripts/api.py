import requests
import urllib3
import logging
from enum import Enum
from base64 import b64encode
from time import sleep
from constants import *

log = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Client(Enum):
    LEAGUE_CLIENT = 1
    RIOT_CLIENT = 2

class Connection:
    def __init__(self):
        self.client_type = ''
        self.client_username = ''
        self.client_password = ''
        self.procname = ''
        self.pid = ''
        self.host = ''
        self.port = ''
        self.protocol = ''
        self.session = ''
        self.headers = ''

    def init(self, client_type: Client):
        self.client_type = client_type
        if self.client_type == Client.LEAGUE_CLIENT:
            self.connect_lcu()
        else:
            self.connect_rc()

    def connect_lcu(self):
        log.info("Connecting to LCU API")
        self.host = LCU_HOST
        self.client_username = LCU_USERNAME

        # lockfile
        lockfile = open(LEAGUE_CLIENT_LOCKFILE_PATH, 'r')
        data = lockfile.read()
        log.debug(data)
        lockfile.close()
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # session
        self.session = requests.session()

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass)}
        log.debug(self.headers['Authorization'])

        # connect
        for i in range(15):
            sleep(1)
            r = self.request('get', '/lol-login/v1/session')
            if r.json()['state'] == 'SUCCEEDED':
                log.debug(r.json())
                log.info("Connection Successful")
                self.request('post', '/lol-login/v1/delete-rso-on-close')  # ensures logout after close
                return

        log.error("Could not connect to League Client")

    def connect_rc(self):
        log.debug("Initializing Riot Client session")
        self.host = RCU_HOST
        self.client_username = RCU_USERNAME

        # lockfile
        lockfile = open(RIOT_CLIENT_LOCKFILE_PATH, 'r')
        data = lockfile.read()
        log.debug(data)
        lockfile.close()
        data = data.split(':')
        self.procname = data[0]
        self.pid = data[1]
        self.port = data[2]
        self.client_password = data[3]
        self.protocol = data[4]

        # session
        self.session = requests.session()

        # headers
        userpass = b64encode(bytes('{}:{}'.format(self.client_username, self.client_password), 'utf-8')).decode('ascii')
        self.headers = {'Authorization': 'Basic {}'.format(userpass), "Content-Type": "application/json"}
        log.debug(self.headers['Authorization'])

    def request(self, method, path, query='', data=''):
        if not query:
            url = "{}://{}:{}{}".format(self.protocol, self.host, self.port, path)
        else:
            url = "{}://{}:{}{}?{}".format(self.protocol, self.host, self.port, path, query)

        if 'username' not in data:
            log.debug("{} {} {}".format(method.upper(), url, data))
        else:
            log.debug("{} {}".format(method.upper(), url))

        fn = getattr(self.session, method)

        if not data:
            r = fn(url, verify=False, headers=self.headers)
        else:
            r = fn(url, verify=False, headers=self.headers, json=data)
        return r