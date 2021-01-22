from enum import Enum, auto


class Channel(Enum):
    orderbook = auto()
    trades = auto()
    ticker = auto()
    fills = auto()
    orders = auto()
