from CodeEntrance import language_grabber
from Discord import reaction_manager, output_manager
from Storage import storage_manager
from Storage.storage_manager import CellStatus


class LanguageManager:
    _language = None
    bot = None
    _language_classes = {}
    _language_descriptions = {}
    _alive_languages = {}
    innput_manager = None


    def __init__(self, bot):
        language_classes, languages = language_grabber.get_languages(self.output_stream, bot.im)
        for i in range(len(languages)):
            self._alive_languages[languages[i].name] = languages[i]
            self._language_descriptions[languages[i].name] = languages[i].description
            self._language_classes[languages[i].name] = language_classes[i]
        self._language = self._alive_languages["sqlite3"]
        self.input_manager = bot.im
        self.bot = bot

    def list_languages(self):
        return self._language_descriptions

    def current_language(self):
        return self._language.name, self._language.description

    def is_available_language(self, l):
        return l in self._alive_languages.keys()

    def switch_language(self, l):
        self._language = self._alive_languages[l]


    async def reset(self):
        await self.halt_all()
        name = self._language.name
        self._language.close()
        del self._alive_languages[name]
        del self._language
        self._alive_languages[name] = self._language_classes[name](self.output_stream, self.bot.im)
        self._language = self._alive_languages[name]

    async def halt_all(self):
        cell_ids = self._language.get_active_cells()
        for id in cell_ids:
            msg = storage_manager.get_msg_by_id(id)
            guild_id = msg.guild_id
            channel_id = msg.channel_id
            message_id = msg.message_id
            await self.halt_execution(guild_id, channel_id, message_id)

    async def output_stream(self, cell_id, result):
        code_cell_msg = storage_manager.get_msg_by_id(cell_id)
        output_or_none = storage_manager.get_associated_output_or_none(code_cell_msg.guild_id,
                                                                       code_cell_msg.channel_id,
                                                                       code_cell_msg.message_id)
        guild = await self.bot.fetch_guild(code_cell_msg.guild_id)
        channel = await guild.fetch_channel(code_cell_msg.channel_id)
        if output_or_none is None:

            output_msg = await output_manager.create_output_msg(channel)
            storage_manager.add_output_cell(guild_id=output_msg.guild.id,
                                            channel_id=output_msg.channel.id,
                                            message_id=output_msg.id,
                                            temp=True)
            await output_manager.print_out(output_msg, result)
        else:
            output_msg = storage_manager.get_msg_by_id(output_or_none.msg_id)
            if output_msg is None:
                return
            message = await channel.fetch_message(output_msg.message_id)
            await output_manager.print_out(message, result)



    async def submit_cell(self, guild_id, channel_id, message_id, message):
        cell_id = storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.submitted)
        result = await self._language.submit(cell_id, message)
        if result is True:
            storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.accepted)
        else:
            storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.rejected)
        return result

    async def run_cell(self, message, guild_id, channel_id, message_id):
        cell = storage_manager.get_code_cell(guild_id, channel_id, message_id)
        if cell.status == CellStatus.accepted:
            await message.add_reaction(reaction_manager.ENQUEUED_INDICATOR)
            # storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.running)
            await self._language.run_cell(cell.msg_id, guild_id, channel_id, message_id, message)
        await message.clear_reactions()
        await message.add_reaction(reaction_manager.FINISHED_NOTIFICATION)
        storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.computed)

    async def halt_execution(self, guild_id, channel_id, message_id):
        guild = await self.bot.fetch_guild(guild_id)
        channel = await guild.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)

        await message.clear_reactions()
        cell = storage_manager.get_code_cell(guild_id, channel_id, message_id)
        await message.add_reaction(reaction_manager.HALT_BUTTON)
        await self._language.halt(cell.msg_id)
        storage_manager.set_msg_status(guild_id, channel_id, message_id, CellStatus.computed)

    async def execute(self, guild_id, channel_id, message_id):
        guild = await self.bot.fetch_guild(guild_id)
        channel = await guild.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)

        await message.clear_reactions()

        result = await self.submit_cell(guild_id, channel_id, message_id, message)
        if result is True:
            # await message.add_reaction(reaction_manager.ENQUEUED_INDICATOR)
            await self.run_cell(message, guild_id, channel_id, message_id)

        else:
            await message.add_reaction(reaction_manager.COMPILATION_ERROR_NOTIFICATION)

    async def halt(self, guild_id, channel_id, message_id):
        await self.halt_execution(guild_id, channel_id, message_id)