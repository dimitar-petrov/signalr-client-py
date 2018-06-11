class EventHook(object):
    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    async def fire(self, *args, **kwargs):
        for handler in self._handlers:
            await handler(*args, **kwargs)

    async def __call__(self, *args, **kwargs):
        await self.fire(*args, **kwargs)
