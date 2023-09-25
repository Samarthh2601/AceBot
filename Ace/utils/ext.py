import os
from datetime import datetime, timedelta
from typing import Any, List

import discord
from discord import app_commands
from discord.colour import Colour
from discord.types.embed import EmbedType
from typing_extensions import Self

from .colours import Colour
from .dtclasses import MessageContent


def get_id(id_or_link: str | int, /) -> int | None:
    if len(id_or_link) in (19, 20,) and id_or_link.isdigit():
        message_id = id_or_link

    elif len(id_or_link) == 88 and not id_or_link.isdigit() and id_or_link.startswith("https://discord.com/channels/"):
        message_id = id_or_link.split("/")[-1]
    else:
        return None

    return int(message_id)

async def get_message_assets(message: discord.Message) -> MessageContent:
    ret = MessageContent()
    if message.content:
        ret.content = message.content

    if message.attachments:
        attachment = message.attachments[0]
        ret.file_url = attachment.url

    if message.embeds:
        embed = message.embeds[0]
        ret.embed = True
        ret.embed_title = "No Title" if embed.title is None else embed.title
        ret.embed_description = "No Description" if embed.description is None else embed.description
        ret.embed_content = f"**Title**: {ret.embed_title}\n**Description**: {ret.embed_description}"

    return ret

def create_message_asset_embed(message: discord.Message):
    embed = Embed()
    if message.content:
        embed.description = f"**Message Content**: {message.content}" 
    embed.add_field("Attachment", "True" if message.attachments else "False") 
    embed.add_field("Embed content", message.embeds[0].description) if message.embeds else ...
    embed.add_field("Server", message.guild.name)
    embed.add_field("Channel", message.channel)
    embed.add_field("Message author", message.author)
    embed.add_field("Message", f"[Click Here]({message.jump_url})")
    embed.set_image(message.attachments[0].url) if message.attachments else ...
    return embed

def generate_timestamp(dt: datetime = None, *, style: str = "f", weeks: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0) -> str:
    if dt is None:
        dt = datetime.utcnow()
    return discord.utils.format_dt(dt + timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds), style=style)


def format_path(path: str) -> str:
    path = path.replace("/", ".")

    if path.startswith("."):
        while path.startswith("."):
            path = path.replace(".", "", 1)

    if path.endswith("."):
        return path
    return f"{path}."

def get_all_extension_choices() -> List:
    from .settings import Info
    f_path = format_path(Info.EXTENSIONS_PATH)

    return [app_commands.Choice(name=file[:-3].capitalize(), value=f"{f_path}{file[:-3]}") for file in os.listdir(Info.EXTENSIONS_PATH) if file.endswith(".py") and not file.startswith("_")]


class Embed(discord.Embed):
    def __init__(self, *, title: Any | None = None, type: EmbedType = 'rich', url: Any | None = None, description: Any | None = None, colour: discord.Colour = None, timestamp: datetime | None = None):
        super().__init__(colour=colour or Colour.random(), color=None, title=title, type=type, url=url, description=description, timestamp=timestamp)
    
    def add_field(self, name: Any, value: Any, inline: bool = False) -> Self:
        return super().add_field(name=name, value=value, inline=inline)
    
    def set_image(self, url: Any | None) -> Self:
        return super().set_image(url=url)

    def set_thumbnail(self, url: Any | None) -> Self:
        return super().set_thumbnail(url=url)