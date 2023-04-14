"""
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
async def connect(connection):
    print("LCU API Connected")


@connector.close
async def disconnect(_):
    print("Client Closed")
    # await connector.stop()

@connector.ws.register('/')
async def event_listener(connection, event):
    for skip_text in ignore:
        if skip_text in event.uri:
            return
    print("\n{}".format(event.uri))
    print(event.data)

connector.start()
