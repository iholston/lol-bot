import subprocess

import psutil
import re

# Regex
LCU_PORT_KEY = "--app-port="
LCU_TOKEN_KEY = "--remoting-auth-token="
PORT_REGEX = re.compile(r"--app-port=(\d+)")
TOKEN_REGEX = re.compile(r"--remoting-auth-token=(\S+)")

# Commands
LAUNCH_CLIENT = r'"C:\Riot Games\Riot Client\RiotClientServices" --launch-product=league_of_legends --launch-patchline=live'

IS_GAME_INSTALLED = f'if exist "C:\Riot Games\League of Legends" (exit 0) else (exit 1)'
IS_GAME_RUNNING = 'tasklist | findstr /r /i "\<League of Legends\>"'
IS_CLIENT_RUNNING = 'tasklist | findstr /i "LeagueClient"'
IS_LAUNCHER_RUNNING = 'tasklist | findstr /i "Riot"'

CLOSE_GAME = 'taskkill /F /IM "League of Legends.exe"'
CLOSE_CLIENT = 'taskkill /F /IM League*'
CLOSE_LAUNCHER = 'taskkill /F /IM Riot*'
CLOSE_ALL = f"{CLOSE_LAUNCHER} & {CLOSE_CLIENT}"


def run(command: str) -> bool:
    if 'launch' in command:
        subprocess.Popen(command)
        return True
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.returncode == 0


def get_auth_string() -> str:
    stdout = ''
    for proc in psutil.process_iter(['name', 'cmdline']):
        if proc.info['name'] == "LeagueClientUx.exe":
            stdout = " ".join(proc.info['cmdline'])
        elif proc.info['name'] == "Riot Client.exe" and PORT_REGEX.search(str(proc.info['cmdline'])):
            stdout = " ".join(proc.info['cmdline'])

    port_match = PORT_REGEX.search(stdout)
    port = port_match.group(1).replace(LCU_PORT_KEY, '') if port_match else "0"

    token_match = TOKEN_REGEX.search(stdout)
    token = token_match.group(1).replace(LCU_TOKEN_KEY, '').replace('"', '') if token_match else ""

    return f"https://riot:{token}@127.0.0.1:{port}"
