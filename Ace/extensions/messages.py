import random
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from ..core import Ace
from ..utils import (BookmarkView, Embed, Record, generate_timestamp,
                     get_message_assets, get_id, create_message_asset_embed)


class Messages(commands.GroupCog, name="message"):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot

    def get_current_tracking_ftstring(self, records: list[Record] | Record):
        if isinstance(records, list):
            return "\n- ".join([f"https://discord.com/channels/{message.guild_id}/{message.channel_id}/{message.message_id} ({message.message_id})" for message in records])
        return f"https://discord.com/channels/{records.guild_id}/{records.channel_id}/{records.message_id}"

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

    @app_commands.command(name="vent", description="Vent in the current server!")
    async def vent(self, inter: discord.Interaction, text: str, name: str=None, avatar: discord.Attachment=None) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        if inter.guild is None:
            return await inter.edit_original_response(content="Please use this command in a server!")  
        channels = await self.bot.db.channels.create(inter.guild.id)
        if channels.vent == 0:
            return await inter.edit_original_response(content="A channel in the server has not been set yet!")

        name = name or f"Anonymous[{random.randint(200, 300)}]"
        _avatar = None

        if avatar:
            _avatar = await avatar.read()
    
        channel = await self.bot.features.getch_channel(channels.vent)
        webhook = await channel.create_webhook(name=name, avatar=_avatar)        
        embed = Embed(description=text)
        await webhook.send(embed=embed)
        await inter.edit_original_response(content=f"Successfully vented in {channel.mention}")

    @app_commands.command(name="track", description="Track a message!")
    async def track(self, inter: discord.Interaction, id_or_link: str, message_channel: discord.TextChannel) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)
        
        if (message_id:=get_id(id_or_link)) is None:
            return await inter.edit_original_response(content="Invalid message ID/link!")

        if (await self.bot.db.messages.read_user_message(inter.user.id, message_id)):
            return await inter.edit_original_response(content="You're already tracking that message!")
        
        if (limit:=(await self.bot.db.messages.read_user(inter.user.id))):
            if len(limit) >= 3:
                embed = Embed(title="Currently tracking messages!", description=self.get_current_tracking_ftstring(limit))
                return await inter.edit_original_response(content="You are already tracking **3** messages! You can only track **3** messages at a time!", embed=embed)

        message = await message_channel.fetch_message(message_id)

        await inter.edit_original_response(content=f"Now tracking [this]({self.get_current_tracking_ftstring(Record(message_id, inter.user.id, message_channel.guild.id, message_channel.id))}) message!")

        embed = create_message_asset_embed(message)
        m = await inter.user.send(embed=embed)
        await self.bot.db.messages.create(inter.user.id, message_channel.id, message_id, message_channel.guild.id, m.id, m.channel.id)

    @app_commands.command(name="untrack", description="Untrack a message!")
    async def untrack(self, inter: discord.Interaction, id_or_link: str) -> discord.InteractionMessage | None:
        await inter.response.defer(ephemeral=True, thinking=True)

        if (message_id:=get_id(id_or_link)) is None:
            return await inter.edit_original_response(content="Invalid message ID/link!")

        if (message:=await self.bot.db.messages.remove(inter.user.id, message_id)) is False:
            return await inter.edit_original_response(content="Could not find any tracked messages with that ID/link")

        await inter.edit_original_response(content=f"Successfully untracked [this]({self.get_current_tracking_ftstring(Record(message_id, inter.user.id, message.guild_id, message.channel_id))}) message!")

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
        embed = Embed(title="Currently tracking messages!", description=self.get_current_tracking_ftstring(i))
        await inter.edit_original_response(embed=embed)

async def setup(bot: Ace):
    await bot.add_cog(Messages(bot))