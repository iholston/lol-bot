import requests
import urllib3
import os
import logging
import client
import subprocess
import re
from base64 import b64encode
from time import sleep
from constants import *

log = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Connection:
    def __init__(self):
        # LCU Vars
        self.lcu_host = LCU_HOST
        self.lcu_port = ''
        self.lcu_protocol = DEFAULT_PROTOCOL
        self.lcu_username = LCU_USERNAME
        self.lcu_password = ''
        self.lcu_session = ''
        self.lcu_headers = ''
        self.lcu_procname = ''
        self.lcu_pid = ''

    def init(self):
        log.info("Connecting to LCU API")

        res = get_league_client_commandline()

        self.lcu_procname = 0
        self.lcu_pid = 0
        self.lcu_port = res[0]
        self.lcu_password = res[1]
        self.lcu_protocol = 'https'

        # Prepare Requests
        log.debug('{}:{}'.format(self.lcu_username, self.lcu_password))
        userpass = b64encode(bytes('{}:{}'.format(
            self.lcu_username, self.lcu_password), 'utf-8')).decode('ascii')
        self.lcu_headers = {'Authorization': 'Basic {}'.format(userpass)}
        log.debug(self.lcu_headers['Authorization'])

        # Create Session
        self.lcu_session = requests.session()

        for i in range(15):
            sleep(1)
            r = self.request('get', '/lol-login/v1/session')
            if r.status_code != 200:
                log.info("Connect request failed: {}".format(r.status_code))
                continue

            if r.json()['state'] == 'SUCCEEDED':
                log.debug(r.json())
                log.info("Connection Successful\n")
                return
            else:
                log.info("Connection status failure: {}".format(
                    r.json()['state']))

        raise client.ClientError

    def request(self, method, path, query='', data=''):
        if not query:
            url = "{}://{}:{}{}".format(self.lcu_protocol,
                                        self.lcu_host, self.lcu_port, path)
        else:
            url = "{}://{}:{}{}?{}".format(self.lcu_protocol,
                                           self.lcu_host, self.lcu_port, path, query)

        log.debug("{} {} {}".format(method.upper(), url, data))

        fn = getattr(self.lcu_session, method)

        if not data:
            r = fn(url, verify=False, headers=self.lcu_headers)
        else:
            r = fn(url, verify=False, headers=self.lcu_headers, json=data)
        return r


def get_league_client_commandline():
    command = "powershell.exe"
    args = ["Get-CimInstance", "Win32_Process", "-Filter", '"name = \'LeagueClientUx.exe\'"', "|",
            "Select-Object", "-ExpandProperty", "CommandLine"]
    process = subprocess.Popen([command] + args, stdout=subprocess.PIPE)
    result = process.communicate()[0].decode("utf-8")
    pattern = re.compile(r"""--app-port=(?P<app_port>\d+)""")
    match = pattern.search(result)
    app_port = match.group("app_port")  
    pattern = re.compile(r"""--remoting-auth-token=(?P<token>\w+)""") 
    match = pattern.search(result)
    remoting_auth_token = match.group("token") 
    return app_port, remoting_auth_token