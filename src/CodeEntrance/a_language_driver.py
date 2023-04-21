import asyncio

from Discord import reaction_manager
from Storage import storage_manager
from Storage.cell_storage import CellStatus


class ALanguageDriver:

    _cells = {}
    _tasks = {}
    _output_stream = None
    _input_manager = None
    name = "-Unspecified Name-"
    description = "-Unspecified Description-"
    lock = None
    _current_line = None

    def __init__(self, output_stream, input_manager, name, uses_queue=False):
        self._output_stream = output_stream
        self._input_manager = input_manager
        self.name = name
        if uses_queue:
            self.lock = asyncio.Lock()

    async def compile(self, code):
        pass

    async def run_compiled_cell(self, cell_content, cell_id):
        pass

    async def run_cell(self, cell_id, guild_id, channel_id, message_id, message):
        self._tasks[cell_id] = asyncio.current_task()
        if self.lock is not None:
            async with self.lock:
                storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.running)
                await message.clear_reactions()
                await message.add_reaction(reaction_manager.RUNNING_INDICATOR)
                await self.run_compiled_cell(self._cells[cell_id], cell_id)
        else:
            storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.running)
            await message.clear_reactions()
            await message.add_reaction(reaction_manager.RUNNING_INDICATOR)
            await self.run_compiled_cell(self._cells[cell_id], cell_id)
        del self._tasks[cell_id]

    async def submit(self, cell_id, code):
        s, b = await self.compile(code.content)
        if b is True:
            self._cells[cell_id] = s
        return b

    async def output(self, cell_id, result):
        await self._output_stream(cell_id, result)

    async def read_line(self):
        if self._current_line is None:
            return await self._input_manager.read_line()
        else:
            c = self._current_line
            self._current_line = None
            return c

    async def read_char(self):
        if self._current_line is None:
            self._current_line = await self._input_manager.read_line()

        c = self._current_line[0]
        if len(self._current_line) > 1:
            self._current_line = self._current_line[1:]
        else:
            self._current_line = None
        return c

    async def flush_input(self):
        await self._input_manager.flush()

    async def halt(self, cell_id):
        try:
            self._tasks[cell_id].cancel()
            del self._tasks[cell_id]
        except KeyError as e:
            pass

    def get_active_cells(self):
        return self._tasks.keys()

    def close(self):
        pass