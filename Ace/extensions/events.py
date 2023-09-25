import discord
from discord import app_commands
from discord.ext import commands

from ..core import Ace
from discord.http import handle_message_parameters

class Events(commands.Cog):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot

    @commands.Cog.listener("on_raw_message_delete")
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        if (records:=await self.bot.db.messages.read_message(payload.message_id)) is None:
            return None
        
        for record in records:
            try:
                await self.bot.http.send_message(record.dm_channel_id, params=handle_message_parameters(content=f"Original message for [this](https://discord.com/channels/@me/{record.dm_channel_id}/{record.dm_id}) message has been deleted!"))
            except discord.Forbidden:
                pass

        await self.bot.db.messages.remove_message(payload.message_id)


async def setup(bot: Ace) -> None:
    await bot.add_cog(Events(bot))