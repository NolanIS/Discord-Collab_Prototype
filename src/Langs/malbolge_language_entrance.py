""" Implementation heavily based on Hunmin Park's (Aventgarde95's) implementation on github:
    pyMalbolge: https://github.com/Avantgarde95/pyMalbolge
"""

from CodeEntrance.a_language_driver import ALanguageDriver

TABLE_CRAZY = (
    (1, 0, 0),
    (1, 0, 2),
    (2, 2, 1)
)

ENCRYPT = list(map(ord,
                   '5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB'
                   '6v^=I_0/8|jsb9m<.TVac`uY*MK\'X~xDl}REokN:#?G\"i@'))

OPS = (
    4,  # jmp [d]
    5,  # out a
    23,  # in a
    39,  # rotr [d] - mov a, [d]
    40,  # mov d, [d]
    62,  # crz [d], a
    68,  # nop
    81  # end
)  # Other values are executed the same as nop (68) but arn't allowed in the source code


def rotate(n):
    return 3 ** 9 * (n % 3) + n / 3


def crazy(a, b):
    result = 0
    d = 1
    for i in range(10):
        result += TABLE_CRAZY[int((b / d) % 3)][int((a / d) % 3)] * d
        d *= 3

    return result

def is_whitespace(character):
    if character == ' ' or character == '\n':
        return True
    return False

class MalbolgeEntrance(ALanguageDriver):
    """ Implementation heavily based on Hunmin Park's (Aventgarde95) implementation on github:
        pyMalbolge: https://github.com/Avantgarde95/pyMalbolge
    """



    def __init__(self, output_stream, input_manager):
        ALanguageDriver.__init__(self, output_stream=output_stream,input_manager=input_manager, name="malbolge", uses_queue=True)
        self.description = """ A simple implementation of Ben Olmstead's esotaric programming language: Malbolge"""

    async def compile(self, code):
        mem = [0] * 3**10
        i = 0
        for c in code:
            if is_whitespace(c):
                continue    # Whitespace is ignored? that means i isn't incremented right?
            if (ord(c) + i) % 94 not in OPS:
                return "Invalid Character", False
            if i == 3**10:
                return "Source is too long", False
            mem[i] = ord(c) # (ord(c) + i) % 98 must be in OPS, but memory is filled with source (c) if it is
            i = i + 1
        while i < 3**10:
            mem[i] = crazy(mem[i - 1], mem[i - 2])  # Memory is filled with 0s so there is no indexing error threat
            i = i + 1
        return mem, True



    async def run_compiled_cell(self, mem, cell_id):
        a = 0   # accumulator
        c = 0   # code pointer -> points to the current instruction
        d = 0   # data pointer -> used for data manipulation -> incremented after every instruction
        await self.flush_input()
        while True:
            if mem[c] < 33 or mem[c] > 126:
                return
            v = (mem[c] + c) % 94

            if v == 4:  # jmp [d]
                c = mem[d]
            elif v == 5:  # out a
                await self.output(cell_id, chr(int(a % 256)))
            elif v == 23:  # in a
                a = ord(await self.read_char())
            elif v == 39:  # rotr[d]; mov a, [d]
                a = mem[d] = rotate(mem[d])
            elif v == 40:  # mov d, [d]
                d = mem[d]
            elif v == 62:  # crz [d], a; mov a, [d]
                a = mem[d] = crazy(a, mem[d])
            # elif v == 68:                   # nop
            #     pass
            elif v == 81:  # end
                return
            else:
                pass

            if 33 <= mem[c] <= 126:
                mem[c] = ENCRYPT[mem[c] - 33]

            c = 0 if c == 3**10 - 1 else c + 1
            d = 0 if d == 3**10 - 1 else d + 1

