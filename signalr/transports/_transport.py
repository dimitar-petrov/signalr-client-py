from abc import abstractmethod
from urllib.parse import quote_plus

try:
    import ujson as json
except ImportError:
    import json


class Transport:
    def __init__(self, session, connection):
        self._session = session
        self._connection = connection

    @abstractmethod
    def _get_name(self):
        pass

    async def negotiate(self):
        url = self.__get_base_url(
            self._connection,
            'negotiate',
            connectionData=self._connection.data)
        negotiate = await self._session.get(url)

        negotiate.raise_for_status()

        return await negotiate.json()

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def send(self, data):
        pass

    @abstractmethod
    async def close(self):
        pass

    def accept(self, negotiate_data):
        return True

    async def _handle_notification(self, message):
        if len(message) > 0:
            data = json.loads(message)
            await self._connection.received.fire(**data)

    def _get_url(self, action, **kwargs):
        args = kwargs.copy()
        args['transport'] = self._get_name()
        args['connectionToken'] = self._connection.token
        args['connectionData'] = self._connection.data

        return self.__get_base_url(self._connection, action, **args)

    @staticmethod
    def __get_base_url(connection, action, **kwargs):
        args = kwargs.copy()
        args.update(connection.qs)
        args['clientProtocol'] = connection.protocol_version
        query = '&'.join([
            '{key}={value}'.format(key=key, value=quote_plus(args[key]))
            for key in args
        ])

        return '{url}/{action}?{query}'.format(
            url=connection.url, action=action, query=query)
