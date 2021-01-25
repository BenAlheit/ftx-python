import asyncio

from ftx_python.stream import FtxWebsocketClient
from ftx_python.stream import Subscription
from ftx_python.stream.channel import Channel


def print_it(data):
    print(data)


def print_it_ob(data, ob):
    print(data, ob)


c = FtxWebsocketClient(subscriptions=[Subscription(Channel.ticker, 'BTC/USDT'),
                                      Subscription(Channel.orderbook, 'BTC/USDT')],
                       hooks={Channel.ticker.name: print_it,
                              Channel.orderbook.name: print_it_ob})


l = asyncio.get_event_loop()
l.create_task(c.run())
l.run_forever()
