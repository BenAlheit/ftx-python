from ftx_python.stream.channel import Channel


class Subscription:

    def __init__(self, channel: Channel, market: str = None) -> None:
        self.channel = channel.name
        if market:
            self.market = market
