from discord import ClientException
from discord.ext.commands import Bot

from Discord import output_manager
from Discord.collab_commands import CollabCommands
from Discord.input_manager import InputManager
from Discord.language_manager import LanguageManager
from Discord.reaction_manager import ReactionManager
from Storage import storage_manager


class CollabBot(Bot):

    lm = None
    im = None

    def __init__(self, command_prefix, intents, self_bot=False):
        Bot.__init__(self, command_prefix=command_prefix, self_bot=self_bot, intents=intents)





    async def clear_reactions(self):
        cells = storage_manager.get_all_code_cells()
        for cell in cells:
            guild = await self.fetch_guild(cell.guild_id)
            channel = await guild.fetch_channel(cell.channel_id)
            message = await channel.fetch_message(cell.message_id)
            await message.clear_reactions()
            storage_manager.remove_code_cell(cell)

    async def remove_temp_output_cells(self):
        cells = storage_manager.get_temp_output_cells()
        for cell in cells:
            guild = await self.fetch_guild(cell.guild_id)
            channel = await guild.fetch_channel(cell.channel_id)
            message = await channel.fetch_message(cell.message_id)
            await message.delete()
            storage_manager.remove_output_cell(cell)

    async def clear_perm_output_cells(self):
        cells = storage_manager.get_perm_output_cells()
        for cell in cells:
            guild = await self.fetch_guild(cell.guild_id)
            channel = await guild.fetch_channel(cell.channel_id)
            message = await channel.fetch_message(cell.message_id)
            await output_manager.clear_output(message)

    async def on_ready(self):
        self.im = InputManager(self)
        self.lm = LanguageManager(self)
        try:
            await self.add_cog(CollabCommands(self))
            await self.add_cog(ReactionManager(self))
            await self.add_cog(self.im)
        except ClientException:
            print("Bot already added exception")
        await self.clear_reactions()
        await self.remove_temp_output_cells()
        await self.clear_perm_output_cells()


        print("All set up!")