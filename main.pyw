"""
Application entry point.
"""


if __name__ == '__main__':
    import lolbot.system.macos.cmd as cmd

    print(cmd.run(cmd.IS_GAME_RUNNING))


