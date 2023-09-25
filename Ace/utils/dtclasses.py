from dataclasses import dataclass

@dataclass
class Account:
    user_id: int
    wallet: int = 1000
    bank: int = 2500

@dataclass
class Channels:
    guild_id: int
    welcome: int
    leave: int
    log: int
    vent: int

@dataclass
class Rank:
    user_id: int
    guild_id: int
    experience: int = 10
    level: int = 1

@dataclass
class GuildInfo:
    guild_id: int
    kick_threshold: int
    ban_threshold: int
    on_join_role: int

@dataclass
class WarnRecord:
    user_id: int
    guild_id: int
    warns: int

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
class PlayerState:
    hp: int
    shield: int
    meds: int
    spare_shields: int
    perks: list

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