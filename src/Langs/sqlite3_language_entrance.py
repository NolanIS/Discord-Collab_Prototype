import sqlite3

from CodeEntrance.a_language_driver import ALanguageDriver


class Sqlite3LanguageEntrance(ALanguageDriver):

    _connection = None
    _cursor = None

    _temp_database = ":memory:"

    def __init__(self, output_stream, input_manager):
        self._connection = sqlite3.connect(self._temp_database)
        self._cursor = self._connection.cursor()
        ALanguageDriver.__init__(self, output_stream=output_stream,input_manager=input_manager, name="sqlite3", uses_queue=True)
        self.description = "A simple sqlite3 runtime. All tables are stored in memory."

    async def compile(self, code):
        return code, True # No parse errors needed for slite3 SQL queries, only runtime errors

    async def run_compiled_cell(self, cell_content, cell_id):
        try:
            res = self._cursor.execute(cell_content)
            # res = self._cursor.executemany(cell_content, [])
        except sqlite3.Error as e:
            await self.output(cell_id, str(e) + '\n')
            return
        result = res.fetchall()
        self._connection.commit()
        await self.output(cell_id, str(result) + '\n')

    def close(self):
        self._cursor.close()
        self._connection.close()