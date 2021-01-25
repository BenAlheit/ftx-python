import asyncio

import websockets

from ftx_python.stream.channel import Channel
from ftx_python.stream.subscription import Subscription

import json

from typing import Union, Dict, DefaultDict

import warnings

import time

import hmac

from collections import defaultdict

from itertools import zip_longest

import zlib

import logging


class FtxWebsocketClient:
    _ENDPOINT = 'wss://ftx.com/ws/'
    _PING_INTERVAL = 15

    def __init__(self, subscriptions: [Union[Subscription, dict]], hooks: {Channel: callable}, api_key: str = None,
                 api_secret: str = None) -> None:
        self._subscriptions = subscriptions
        self._hooks = hooks
        self._api_key = api_key
        self._api_secret = api_secret
        self._ws = None
        self._orderbooks: DefaultDict[str, Dict[str, DefaultDict[float, float]]] = defaultdict(
            lambda: {side: defaultdict(float) for side in {'bids', 'asks'}})

    @property
    def orderbooks(self) -> Dict:
        return self._orderbooks.copy()

    async def _send_json(self, msg: Dict) -> None:
        if self._ws is None:
            raise Exception(f'Trying to send message {msg} but the websocket is not connected.')

        await self._ws.send(json.dumps(msg))

    async def _subscribe(self, subscription: Dict) -> None:
        await self._send_json({'op': 'subscribe', **subscription})

    async def _unsubscribe(self, subscription: Dict) -> None:
        await self._send_json({'op': 'unsubscribe', **subscription})

    async def _login(self) -> None:
        ts = int(time.time() * 1000)
        await self._send_json({'op': 'login',
                               'args': {
                                   'key': self._api_key,
                                   'sign': hmac.new(self._api_secret.encode(),
                                                    f'{ts}websocket_login'.encode(),
                                                    'sha256').hexdigest(),
                                   'time': ts}
                               })

    def _reset_orderbook(self, market: str) -> None:
        if market in self._orderbooks:
            del self._orderbooks[market]

    async def _handle_orderbook_message(self, message: Dict) -> None:
        market = message['market']

        data = message['data']
        if data['action'] == 'partial':
            self._reset_orderbook(market)

        for side in {'bids', 'asks'}:
            book = self._orderbooks[market][side]
            for price, size in data[side]:
                if size:
                    book[price] = size
                else:
                    del book[price]

        checksum = data['checksum']
        orderbook = self._orderbooks[market]

        bid_prices = sorted(orderbook['bids'].keys(), reverse=True)[:100]
        bids = zip(bid_prices, (orderbook['bids'][price] for price in bid_prices))

        ask_prices = sorted(orderbook['asks'].keys())[:100]
        asks = zip(ask_prices, (orderbook['asks'][price] for price in ask_prices))

        checksum_data = [
            ':'.join([f'{float(order[0])}:{float(order[1])}' for order in (bid, offer) if order])
            for (bid, offer) in zip_longest(bids, asks)
        ]

        computed_result = int(zlib.crc32(':'.join(checksum_data).encode()))
        if computed_result != checksum:
            self._reset_orderbook(market)
            await self._unsubscribe({'market': market, 'channel': 'orderbook'})
            await self._subscribe({'market': market, 'channel': 'orderbook'})

    async def run(self) -> None:
        async with websockets.connect(self._ENDPOINT, ssl=True, ping_interval=self._PING_INTERVAL) as self._ws:

            if None not in [self._api_key, self._api_secret]:
                await self._login()

            for subscription in self._subscriptions:
                subs_dict = subscription.__dict__ if isinstance(subscription, Subscription) else subscription

                if subs_dict['channel'] in ['fills', 'orders'] and None in [self._api_key, self._api_secret]:
                    raise Exception(f'An API key and secret needs to be provided to access the {subs_dict["channel"]} '
                                    f'channel.')

                await self._subscribe(subs_dict)

            async for message in self._ws:
                data = json.loads(message)
                if 'channel' in data.keys():
                    if data['channel'] == 'orderbook' and data['type'] not in ['subscribed', 'unsubscribed']:
                        await self._handle_orderbook_message(data)

                    if data['channel'] in self._hooks.keys():
                        func = self._hooks[data['channel']]

                        args = (data, self.orderbooks[data['market']]) if data['channel'] == 'orderbook' else (data,)
                        if asyncio.iscoroutinefunction(func):
                            await func(*args)
                        else:
                            func(*args)

                    else:
                        warnings.warn(f'No hook provided for {data["channel"]} channel.')
                else:
                    logging.info(data)
