from discord.ext.commands import Cog

from Discord import output_manager
from Storage import storage_manager
from Storage.storage_manager import CellStatus

SUBMIT_BUTTON = "▶️"
FINISHED_NOTIFICATION = "✅"
COMPILATION_ERROR_NOTIFICATION = "❌"
ENQUEUED_INDICATOR = "🕒"
RUNNING_INDICATOR = "🎮"
EDITED_CELL_NOTIFICATION = "🔁"
HALT_BUTTON = "🟥"

CLEAR_OUTPUT_BUTTON = "🧹"
REMOVE_OUTPUT_BUTTON = "🗑️"

class ReactionManager(Cog):



    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        emoji = payload.emoji

        guild = await self.bot.fetch_guild(payload.guild_id)
        channel = await guild.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if emoji.name == SUBMIT_BUTTON:
            await self.bot.lm.execute(payload.guild_id, payload.channel_id, payload.message_id)
        if emoji.name == HALT_BUTTON:
            await self.bot.lm.halt(payload.guild_id, payload.channel_id, payload.message_id)


        if emoji.name == CLEAR_OUTPUT_BUTTON:
            await message.clear_reactions()
            await output_manager.clear_output(message)
        if emoji.name == REMOVE_OUTPUT_BUTTON:
            await message.clear_reactions()
            await output_manager.remove_output(message)




    @Cog.listener()
    async def on_raw_message_edit(self, payload):
        message_id = payload.message_id

        if not storage_manager.is_code_cell_active(payload.guild_id, payload.channel_id, message_id):
            return

        guild_id = payload.guild_id
        channel_id = payload.channel_id

        guild = await self.bot.fetch_guild(guild_id)
        channel = await guild.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)

        await message.clear_reactions()

        storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.edited)

        await message.add_reaction(EDITED_CELL_NOTIFICATION)
