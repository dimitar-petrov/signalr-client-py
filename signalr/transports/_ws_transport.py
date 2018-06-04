import json
import asyncio
import websockets
from urllib.parse import urlparse, urlunparse
from ._transport import Transport


class WebSocketsTransport(Transport):
    def __init__(self, session, connection):
        Transport.__init__(self, session, connection)
        self.ws = None
        self.__requests = {}
        self._ws_timeout = 10
        self._ping_timeout = 5

    def _get_name(self):
        return 'webSockets'

    @staticmethod
    def __get_ws_url_from(url):
        parsed = urlparse(url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        url_data = (scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)

        return urlunparse(url_data)

    async def consumer(self):
        while True:
            try:
                notification = await asyncio.wait_for(
                    self.ws.recv(), timeout=self._ws_timeout)
            except asyncio.TimeoutError:
                try:
                    pong_waiter = await self.ws.ping()
                    await asyncio.wait_for(
                        pong_waiter, timeout=self._ping_timeout)
                except asyncio.TimeoutError:
                    break
            except websockets.ConnectionClosed:
                break
            else:
                await self._handle_notification(notification)

    async def start(self):
        ws_url = self.__get_ws_url_from(self._get_url('connect'))
        self.ws = await websockets.connect(ws_url)
        asyncio.get_event_loop().create_task(self.consumer())
        # self._session.get(self._get_url('start'))

    async def send(self, data):
        await self.ws.send(json.dumps(data))

    def close(self):
        self.ws.close()

    def accept(self, negotiate_data):
        return bool(negotiate_data['TryWebSockets'])

    class HeadersLoader(object):
        def __init__(self, headers):
            self.headers = headers

    # def __get_headers(self):
    #     headers = self._session._default_headers
    #     loader = WebSocketsTransport.HeadersLoader(headers)

    #     if self._session._default_auth:
    #         self._session.auth(loader)

    #     return ['%s: %s' % (name, headers[name]) for name in headers]

    # def __get_cookie_str(self):
    #     return '; '.join([
    #                          '%s=%s' % (cookie.key, cookie.value)
    #                          for cookie in self._session.cookie_jar])
