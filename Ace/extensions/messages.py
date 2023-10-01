from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from ..core import Ace
from ..utils import (BookmarkView, Embed, Record, generate_timestamp,
                     get_message_assets, get_id, get_current_tracking_ftstring)


class Messages(commands.GroupCog, name="message"):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot

    @app_commands.command(name="bookmark", description="Bookmark a message!")
    async def bookmark(self, inter: discord.Interaction, id_or_link: str) -> None:
        await inter.response.defer()
        message_id = get_id(id_or_link)
        message = await inter.channel.fetch_message(message_id)
        message_content = await get_message_assets(message)
        embed = Embed()
        if message.content:
            embed.description = f"**Message Content**: {message_content.content}" 
        embed.add_field("Attachment", "True" if message.attachments else "False") 
        embed.add_field("Embed content", message_content.embed_content) if message_content.embed is True else ...
        embed.add_field("Server", inter.guild.name)
        embed.add_field("Channel", inter.channel)
        embed.add_field("Message author", message.author)
        embed.add_field("Message", f"[Click Here]({message.jump_url})")
        view = BookmarkView(embed)
        await inter.edit_original_response(content=f"The button below will timeout in {generate_timestamp(datetime.now(), minutes=3, style='R')}", embed=embed, view=view)
        try:
            await inter.user.send(embed=embed)
        except discord.Forbidden:
            await inter.channel.send(f"{inter.user.mention}, Enable your DMs and click the **Copy** button!")


    @app_commands.command(name="track", description="Track a message!")
    async def track(self, inter: discord.Interaction, id_or_link: str, message_channel: discord.TextChannel) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        
        if (message_id:=get_id(id_or_link)) is None:
            return await inter.edit_original_response(content="Invalid message ID/link!")

        if (await self.bot.db.messages.read_user_message(inter.user.id, message_id)):
            return await inter.edit_original_response(content="You're already tracking that message!")
        
        if (limit:=(await self.bot.db.messages.read_user(inter.user.id))):
            if len(limit) >= 3:
                embed = Embed(title="Currently tracking messages!", description=get_current_tracking_ftstring(limit, ft_string=True))
                return await inter.edit_original_response(content="You are already tracking **3** messages! You can only track **3** messages at a time!", embed=embed)

        message = await message_channel.fetch_message(message_id)

        await inter.edit_original_response(content=f"Now tracking [this]({get_current_tracking_ftstring(Record(message_id, inter.user.id, message_channel.guild.id, message_channel.id))}) message!")

        embed = Embed()
        if message.content:
            embed.description = f"**Message Content**: {message.content}" 
        embed.add_field("Attachment", "Yes" if message.attachments else "None") 
        embed.add_field("Embed content", message.embeds[0].description) if message.embeds else ...
        embed.add_field("Server", message.guild.name)
        embed.add_field("Channel", message.channel)
        embed.add_field("Message author", message.author)
        embed.add_field("Message", f"[Click Here]({message.jump_url})")
        embed.set_image(message.attachments[0].url) if message.attachments else ...
        
        m = await inter.user.send(embed=embed)
        await self.bot.db.messages.create(inter.user.id, message_channel.id, message_id, message_channel.guild.id, m.id, m.channel.id)

    @app_commands.command(name="untrack", description="Untrack a message!")
    async def untrack(self, inter: discord.Interaction, id_or_link: str) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)

        if (message_id:=get_id(id_or_link)) is None:
            return await inter.edit_original_response(content="Invalid message ID/link!")

        if (message:=await self.bot.db.messages.remove(inter.user.id, message_id)) is False:
            return await inter.edit_original_response(content="Could not find any tracked messages with that ID/link")

        await inter.edit_original_response(content=f"Successfully untracked [this]({get_current_tracking_ftstring(message)}) message!")

    @app_commands.command(name="untrack_all", description="Untrack all messages!")
    async def untrack_all(self, inter: discord.Interaction) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        if await self.bot.db.messages.read_user(inter.user.id) is None:
            return await inter.edit_original_response(content="You are already not tracking any message!")

        await self.bot.db.messages.remove_user(inter.user.id)
        await inter.edit_original_response(content="Successfully untracked all messages!")        

    @app_commands.command(name="current_tracking", description="Get current tracking messages!")
    async def current_tracking(self, inter: discord.Interaction) -> discord.InteractionMessage | None: 
        await inter.response.defer(ephemeral=True, thinking=True)
        i = await self.bot.db.messages.read_user(inter.user.id)
        if i is None:
            return await inter.edit_original_response(content="You are not tracking any messages!")
        embed = Embed(title="Currently tracking messages!", description=get_current_tracking_ftstring(i, ft_string=True))
        await inter.edit_original_response(embed=embed)

async def setup(bot: Ace):
    await bot.add_cog(Messages(bot))