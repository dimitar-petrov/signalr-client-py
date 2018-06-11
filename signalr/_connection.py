try:
    import ujson as json
except ImportError:
    import json

from signalr.events import EventHook
from signalr.hubs import Hub
from signalr.transports import AutoTransport


class Connection:
    protocol_version = '1.5'

    def __init__(self, url, session):
        self.url = url
        self.__hubs = {}
        self.qs = {}
        self.__send_counter = -1
        self.token = None
        self.data = None
        self.received = EventHook()
        self.error = EventHook()
        self.starting = EventHook()
        self.stopping = EventHook()
        self.__transport = AutoTransport(session, self)
        self.started = False

        async def handle_error(**kwargs):
            error = kwargs["E"] if "E" in kwargs else None
            if error is None:
                return

            await self.error.fire(error)

        self.received += handle_error

        self.starting += self.__set_data

    async def __set_data(self):
        self.data = json.dumps([{
            'name': hub_name
        } for hub_name in self.__hubs])

    def increment_send_counter(self):
        self.__send_counter += 1
        return self.__send_counter

    async def start(self):
        await self.starting.fire()

        negotiate_data = await self.__transport.negotiate()
        self.token = negotiate_data['ConnectionToken']

        await self.__transport.start()

    # def wait(self, timeout=30):
    #     pass
    #     # gevent.joinall([self.__greenlet], timeout)

    async def send(self, data):
        await self.__transport.send(data)

    async def close(self):
        # gevent.kill(self.__greenlet)
        await self.__transport.close()

    def register_hub(self, name):
        if name not in self.__hubs:
            if self.started:
                raise RuntimeError(
                    'Cannot create new hub because connection is already started.'
                )

            self.__hubs[name] = Hub(name, self)
        return self.__hubs[name]

    def hub(self, name):
        return self.__hubs[name]

    def __aenter__(self):
        pass

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
