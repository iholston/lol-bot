import logging
import sys
import traceback
import os
import constants
import client
import account

log = logging.getLogger(__name__)

def main():
    try:
        logging.basicConfig(
            filename=os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + "/logs.txt",
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s',
            datefmt='%d %b %Y %H:%M:%S',
        )
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s'))
        logging.getLogger().addHandler(ch)
    except FileNotFoundError:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s',
            datefmt='%d %b %Y %H:%M:%S',
        )

    print("""\n\n            ──────▄▌▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
            ───▄▄██▌█ BEEP BEEP
            ▄▄▄▌▐██▌█ -15 LP DELIVERY
            ███████▌█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
            ▀(⊙)▀▀▀▀▀▀▀(⊙)(⊙)▀▀▀▀▀▀▀▀▀▀(⊙)\n\n\t\t\tLoL Bot\n\n""")

    errno = 0
    while True:
        try:
            client.init()
            client.loop()
        except client.AccountLeveled:
            client.close()
            account.set_account_as_leveled()
            errno = 0
        except client.ClientError:
            errno += 1
            if errno == constants.MAX_ERRORS:
                log.info("Max errors reached. Exiting.")
                sys.exit()
            client.close()
        except KeyboardInterrupt:
            log.warning("Keyboard Interrupt.")
            sys.exit()
        except:
            log.warning("Unexpected Error: {}".format(traceback.format_exc()))
            sys.exit()

if __name__ == '__main__':
    main()