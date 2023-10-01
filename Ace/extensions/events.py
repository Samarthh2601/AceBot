import discord
from discord.ext import commands

from ..core import Ace
from discord.http import handle_message_parameters
from ..utils import get_current_tracking_ftstring

class Events(commands.Cog):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot

    @commands.Cog.listener("on_raw_message_delete")
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        if (records:=await self.bot.db.messages.read_message(payload.message_id)) is None:
            return None
        
        for record in records:
            try:
                await self.bot.http.send_message(record.dm_channel_id, params=handle_message_parameters(content=f"Original message for [this](https://discord.com/channels/@me/{record.dm_channel_id}/{record.dm_id}) message has been deleted! Get the original message [here]({get_current_tracking_ftstring(records)})!"))
            except discord.Forbidden:
                pass

        await self.bot.db.messages.remove_message(payload.message_id)

    @commands.Cog.listener("on_raw_message_edit")
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        if (records:=await self.bot.db.messages.read_message(payload.message_id)) is None:
            return None

        for record in records:
            try:
                await self.bot.http.send_message(record.dm_channel_id, params=handle_message_parameters(content=f"Original message for [this](https://discord.com/channels/@me/{record.dm_channel_id}/{record.dm_id}) message has been updated! Get the original message [here]({get_current_tracking_ftstring(records)})!"))
            except discord.Forbidden:
                pass

    
    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message) -> discord.Message | None:
        user = await self.bot.db.ranks.create(message.author.id, message.guild.id)
        if user.experience <= 5:
            return None
        if user.experience % 200 == 0:
            await self.bot.db.ranks.update(message.author.id, message.guild.id, xp=user.experience+5, level=user.level+1)
            return await message.author.send(f"You have levelled up to **{user.level+1}** in **{message.guild.name}**")

        await self.bot.db.ranks.update(message.author.id, message.guild.id, xp=user.experience+5)

async def setup(bot: Ace) -> None:
    await bot.add_cog(Events(bot))