import json
import sseclient
from ._transport import Transport


# TODO: This class is not converted to asyncio,
# just added async methods, not to break the
# Transport sublcass
class ServerSentEventsTransport(Transport):
    def __init__(self, session, connection):
        Transport.__init__(self, session, connection)
        self.__response = None

    def _get_name(self):
        return 'serverSentEvents'

    async def start(self):
        self.__response = sseclient.SSEClient(
            self._get_url('connect'), session=self._session)
        self._session.get(self._get_url('start'))

        def _receive():
            for notification in self.__response:
                if notification.data != 'initialized':
                    self._handle_notification(notification.data)

        return _receive

    async def send(self, data):
        response = self._session.post(
            self._get_url('send'), data={'data': json.dumps(data)})
        parsed = json.loads(response.content)
        self._connection.received.fire(**parsed)

    def close(self):
        self._session.get(self._get_url('abort'))
