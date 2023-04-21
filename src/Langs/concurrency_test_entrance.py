import asyncio

from CodeEntrance.a_language_driver import ALanguageDriver


class ConcurrencyTestEntrance(ALanguageDriver):



    def __init__(self, output_stream, input_manager):
        ALanguageDriver.__init__(self, output_stream=output_stream,input_manager=input_manager, name="concurrency_test", uses_queue=False)
        self.description = """ A simple runtime used for debugging. Providing a number, n, will result in m=m+n being printed to the output stream every n seconds, Along with the code cell's ID. """

    async def compile(self, code):
        try:
            x = float(code)
        except ValueError as e:
            return e, False
        return x, True

    async def run_compiled_cell(self, cell_content, cell_id):
        total = 0.0
        while True:
            total = total + float(cell_content)
            await asyncio.sleep(float(cell_content))
            o = str(total) + ", " + str(cell_id)
            await self.output(cell_id, o + "\n")
