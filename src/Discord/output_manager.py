from discord import NotFound

from Storage import storage_manager

pre_fill_map = {}

async def create_output_msg(channel):
    msg = await channel.send(content=("Output:"))
    pre_fill_map[msg.id] = "\n\n"
    return msg

async def edit_output_msg(msg, content):
    old_msg = await msg.fetch()
    old_content = old_msg.content
    pre_fill = ""
    try:
        pre_fill = pre_fill_map[msg.id]
    except KeyError as e:
        pre_fill = "\n\n"
    pre_fill_map[msg.id] = ""
    n_m = old_content + pre_fill + content
    await msg.edit(content=(n_m))

async def print_out(msg, content):
    c, s = scan_out_trailing_whitespace(content)
    try:
        await edit_output_msg(msg, c)
    except NotFound as e:
        return
    pre_fill_map[msg.id] = s

def scan_out_trailing_whitespace(msg_content):
    for i in reversed(range(len(msg_content))):
        if not msg_content[i].isspace():

            return msg_content[0:i+1], msg_content[i+1:]
    return msg_content," "

async def clear_output(msg):
    if storage_manager.get_output_cell_or_none(msg) is not None:
        await msg.edit(content="Output:")
        pre_fill_map[msg.id] = "\n\n"

async def remove_output(msg):
    cell = storage_manager.get_output_cell_or_none(msg)
    if cell is not None:
        storage_manager.remove_output_cell(cell)
        await msg.delete()