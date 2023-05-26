import logging
import sys
import traceback
import client
import game
import account
import os
import constants

log = logging.getLogger(__name__)

def main():
    logging.basicConfig(
        filename=os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + "/log.txt",
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)-7s] [%(funcName)-21s] %(message)s',
        datefmt='%d %b %Y %H:%M:%S',
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

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
        except client.ClientError:
            errno += 1
            if errno == constants.MAX_ERRORS:
                log.info("Max errors reached. Exiting.")
                sys.exit()
            client.close()
        except KeyboardInterrupt:
            log.warning("Keyboard Interrupt.")
            if client.get_phase() == 'InProgress':
                response = input("Game is running. Finish game before exiting? (Y/N) ")
                if response == 'Y' or response == 'y':
                    game.play_game()
                log.info("Game complete. Exiting...")
            else:
                log.info("Exiting...")
            sys.exit()
        except:
            log.warning("Unexpected Error: {}".format(traceback.format_exc()))
            sys.exit()

if __name__ == '__main__':
    main()