"""
Prints out League Client endpoints and return values

Run this while rummaging around the league of legends client to get an
understanding of what endpoints are useful. use in conjunction with
rift explorer/lcu explorer.

You will also need to 'pip install lcu_driver'
"""

from lcu_driver import Connector

connector = Connector()

# any urls you don't want to see
ignore = ['/lol-game-data/assets',
          '/lol-hovercard',
          '/lol-clash',
          '/lol-challenges',
          '/data-store',
          '/lol-patch',
          '/patcher',
          '/lol-tft',
          '/lol-chat',
          '/lol-regalia'
          ]

@connector.ready
async def connect(_) -> None:
    """Displays connection confirmation"""
    print("LCU API Connected")

@connector.ws.register('/')
async def event_listener(_, event) -> None:
    """Prints event info"""
    for skip_text in ignore:
        if skip_text in event.uri:
            return
    print("\n{}\n{}".format(event.uri, event.data))

connector.start()
