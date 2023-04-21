from CodeEntrance.a_language_driver import ALanguageDriver


class CatTestEntrance(ALanguageDriver):



    def __init__(self, output_stream, input_manager):
        ALanguageDriver.__init__(self, output_stream=output_stream, input_manager=input_manager, name="echo_test", uses_queue=False)
        self.description = """ A simple input test. Submit 'cat' to continually read input, Submit 'echo {int}' to read {int} lines of input. """

    async def compile(self, code):
        if code.startswith("echo"):
            if code == "echo":
                return None, True
            else:
                s = code[3:]
                try:
                    x = int(s)
                except ValueError as e:
                    return e, False
                return x, True
        else:
            return "Invalid, insert 'echo {int}?'.", False


    async def run_compiled_cell(self, cell_content, cell_id):
        total = 0
        await self.flush_input()
        while cell_content is None:
            c = await self.read_line()
            print("Echo Test:" + c)
            await self.output(cell_id, c + "\n")
        if cell_content is not None:
            while total < cell_content:
                c = await self.read_line()
                await self.output(cell_id, c + "\n")
                total = total+1;




