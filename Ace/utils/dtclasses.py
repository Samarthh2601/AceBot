from dataclasses import dataclass

@dataclass
class Rank:
    user_id: int
    guild_id: int
    experience: int = 10
    level: int = 1

@dataclass
class Embed:
    embed: bool = False
    embed_title: str = None
    embed_description: str = None
    embed_content: str = None

@dataclass
class MessageContent(Embed):
    content: str = None
    file_url: str = None


@dataclass
class Uptime:
    days: int
    hours: int
    minutes: int
    seconds: int

@dataclass
class Record:
    message_id: int
    user_id: int
    guild_id: int
    channel_id: int=None
    dm_id: int=None
    dm_channel_id: int=None