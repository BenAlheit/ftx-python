import asyncio

from ftx_stream.channel import Channel
from ftx_stream.subscription import Subscription
# from ftx_python import ftx_python
from ftx_stream.ftx_stream import FtxWebsocketClient

def trade_hook(data):
    print('This is your trade hook talking')
    print(data)


def ticker_hook(data):
    print('This is your ticker hook talking')
    print(data)



def orderbook_hook(data, orderbook):
    print('This is your orderbook hook talking')
    # book = client
    print(data)
    print(orderbook)


ws_client = FtxWebsocketClient(subscriptions=[Subscription(Channel.orderbook, 'BTC/USD')],
                               hooks={Channel.trades.name: trade_hook,
                                      Channel.orderbook.name: orderbook_hook,
                                      Channel.ticker.name: ticker_hook})

loop = asyncio.get_event_loop()
loop.run_until_complete(ws_client.run())
