from discord.ext import commands
from discord.ext.commands import Cog

from Discord import reaction_manager, output_manager
from Storage import storage_manager


class CollabCommands(Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def add_output(self, ctx):
        """ adds a permanent output cell"""
        channel = ctx.channel
        msg = await output_manager.create_output_msg(channel)
        storage_manager.add_output_cell(guild_id=msg.guild.id, channel_id=msg.channel.id, message_id=msg.id)

    @commands.command(pass_context=True)
    async def clear(self, ctx):
        """ Clears all output cells"""
        o1 = storage_manager.get_temp_output_cells()
        o2 = storage_manager.get_perm_output_cells()
        for o in o1:
            await output_manager.clear_output(await self.get_msg(o))
        for o in o2:
            await output_manager.clear_output(await self.get_msg(o))

    async def get_msg(self, cell):
        guild = await self.bot.fetch_guild(cell.guild_id)
        channel = await guild.fetch_channel(cell.channel_id)
        message = await channel.fetch_message(cell.message_id)
        return message

    @commands.command(pass_context=True)
    async def remove(self, ctx):
        """ Removes all output cells"""
        o1 = storage_manager.get_temp_output_cells()
        o2 = storage_manager.get_perm_output_cells()
        for o in o1:
            await output_manager.remove_output(await self.get_msg(o))
        for o in o2:
            await output_manager.remove_output(await self.get_msg(o))

    @commands.command(pass_context=True)
    async def languages(self, ctx):
        """ Lists all available language runtimes"""
        l = self.bot.lm.list_languages()
        c = "**Available Language Runtimes: **\n\n"
        for k in l.keys():
            c = c + "**" + k + "**" + ": \n \t" + l[k] + "\n\n"
        await ctx.send(c)

    @commands.command(pass_context=True)
    async def get_language(self, ctx):
        """ Displays the currently active language runtime"""
        n, d = self.bot.lm.current_language()
        c = "**Current Language: ** \n\n **" + n + ": **" + d
        await ctx.send(c)

    @commands.command(pass_context=True)
    async def set_language(self, ctx, *args):
        """ Sets the current language runtime"""
        if len(args) == 0:
            await ctx.send("**Please provide a language name, for example: ** /set_language sqlite3")
        if len(args) > 1:
            await ctx.send("**Please provide a single language name, for example: ** /set_language sqlite3")
        if len(args) == 1:
            n = args[0]
            if self.bot.lm.is_available_language(n):
                self.bot.lm.switch_language(n)
                await ctx.send("**Set language to: " + n + " **")
            else:
                await ctx.send(
                    "There is no runtime available for '" + n + "'. Use **/languages** to get a list of available runtimes")

    @commands.command(pass_context=True)
    async def actions(self, ctx):
        """ Lists all execution actions(buttons) and indicators"""
        c = "Actions and Indicators are emoji's that can be used on a message by reacting to it with the associated emoji \n\n"
        c += reaction_manager.SUBMIT_BUTTON + ": Submits the cell for compilation, then queues it for execution\n"
        c += reaction_manager.HALT_BUTTON + ": Halts the execution of the cell\n"
        c += reaction_manager.CLEAR_OUTPUT_BUTTON + ": Clears the output cell\n"
        c += reaction_manager.REMOVE_OUTPUT_BUTTON + ": Removes the output cell\n"
        c += reaction_manager.COMPILATION_ERROR_NOTIFICATION + ": Indicates that the cell had a compilation error\n"
        c += reaction_manager.ENQUEUED_INDICATOR + ": Indicates that the cell is currently enqueued and awaiting execution\n"
        c += reaction_manager.RUNNING_INDICATOR + ": Indicates that the cell is currently executing\n"
        c += reaction_manager.FINISHED_NOTIFICATION + ": Indicates that the cell has finished executing\n"
        c += reaction_manager.EDITED_CELL_NOTIFICATION + ": Indicates that the cell has been modified since being submitted\n"
        await ctx.send(c)

    @commands.command(pass_context=True)
    async def halt(self, ctx):
        """ Halts the execution of all cells for the active runtime"""
        await self.bot.lm.halt_all()

    @commands.command(pass_context=True)
    async def reset(self, ctx):
        """ Resets the current runtime"""
        await self.bot.lm.reset()