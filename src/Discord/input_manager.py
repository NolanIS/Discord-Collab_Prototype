import asyncio
from asyncio import Queue

from discord.ext.commands import Cog


class InputManager(Cog):
    _messages = None

    def __init__(self, bot):
        self.bot = bot
        self._lock = asyncio.Lock()
        self._messages = Queue()

    async def flush(self):
        while not self._messages.empty():
            self._messages.get_nowait()
            self._messages.task_done()

    async def read_line(self):
        r = await self._messages.get()
        self._messages.task_done()
        return r

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        c = message.content
        await self._messages.put(c)
