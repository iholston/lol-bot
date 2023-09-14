import logging
import sys
import traceback
import os
import constants
import launcher
import client
import utils
import account
from datetime import datetime

log = logging.getLogger(__name__)

def main():
    log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(
        filename=os.path.join(log_dir, datetime.now().strftime('%d%m%Y_%H%M_log.log')),
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s',
        datefmt='%d %b %Y %H:%M:%S',
    )
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s'))
    logging.getLogger().addHandler(ch)

    print("""\n\n            ──────▄▌▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
            ───▄▄██▌█ BEEP BEEP
            ▄▄▄▌▐██▌█ -15 LP DELIVERY
            ███████▌█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
            ▀(⊙)▀▀▀▀▀▀▀(⊙)(⊙)▀▀▀▀▀▀▀▀▀▀(⊙)\n\n\t\t\tLoL Bot\n\n""")

    errno = 0
    while True:
        try:
            launcher.launch_league()
            client.init()
            client.loop()
        except client.AccountLeveled:
            utils.close_processes()
            account.set_account_as_leveled()
            errno = 0
        except (client.ClientError, launcher.LauncherError):
            errno += 1
            if errno == constants.MAX_ERRORS:
                log.info("Max errors reached. Exiting.")
                sys.exit()
            utils.close_processes()
        except launcher.InvalidCredentials:
            log.error("Please update username/password and before restart")
            sys.exit()
        except KeyboardInterrupt:
            log.warning("Keyboard Interrupt.")
            sys.exit()
        except:
            log.warning("Unexpected Error: {}".format(traceback.format_exc()))
            sys.exit()

if __name__ == '__main__':
    main()
