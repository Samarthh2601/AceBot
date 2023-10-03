import os
import platform
from datetime import datetime
from logging import DEBUG, Logger
from typing import List

import colorlog
import discord
from discord.ext import commands

from ..database import DatabaseManager
from ..utils import Info, Uptime, format_path


class BotSetup:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = self.get_logger()
        self._boot_time = datetime.utcnow()

    def get_logger(self) -> Logger:
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s: %(name)s : %(message)s'))
        logger = colorlog.getLogger(Info.LOGGER_NAME)
        logger.addHandler(handler)
        logger.setLevel(DEBUG)
        return logger

    async def _tree_setup(self, guild_id: int) -> List[discord.app_commands.AppCommand]:
        self.bot.tree.on_error = self.on_tree_error
        self.bot.tree.copy_global_to(guild=discord.Object(guild_id))
        return await self.bot.tree.sync()
    
    async def on_tree_error(self, inter: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
        self.logger.error(error.with_traceback(None))

    async def initialize_db(self) -> DatabaseManager:
        db = DatabaseManager()
        await db.setup()        
        return db
    
    def load_info(self) -> None:
        app_commands_groups = self.bot.tree.get_commands()
        self.logger.info("%s is connected to Shard ID %s", self.bot.user, self.bot.shard_id)
        self.logger.info("Application ID: %s", self.bot.user.id)
        self.logger.info("Platform: %s", platform.system())
        self.logger.info("Boot Time (UTC): %s", self._boot_time)
        self.logger.info("App Command Groups Synced: %s", len(app_commands_groups))
        self.logger.info("App Command Groups: %s", ", ".join(group.name for group in app_commands_groups))
    
    @property
    def uptime(self) -> Uptime:
        _upt = int((datetime.utcnow() - self._boot_time).total_seconds())
        hours, remainder = divmod(_upt, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        return Uptime(days, hours, minutes, seconds)


class CustomFeatures:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def load_extensions_from(self, path: str) -> None:
        f_path = format_path(path)
        [await self.bot.load_extension(f"{f_path}{file[:-3]}") for file in os.listdir(path) if file.endswith(".py") and not file.startswith("_")]
    
    async def unload_extensions_from(self, path: str) -> None:
        f_path = format_path(path)
        [await self.bot.unload_extension(f"{f_path}{file[:-3]}") for file in os.listdir(path) if file.endswith(".py") and not file.startswith("_")]
    
    async def reload_extensions_from(self, path: str) -> None:
        await self.unload_extensions_from(path)
        await self.load_extensions_from(path)

    async def getch_user(self, user_id: int) -> discord.User:
        return self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
    
    async def getch_guild(self, guild_id: int) -> discord.Guild:
        return self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
    
    async def getch_channel(self, channel_id: int) -> discord.TextChannel | discord.VoiceChannel:
        return self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)

    async def getch_member(self, guild_id: int, member_id: int) -> discord.Member:
        guild = await self.getch_guild(guild_id)
        return guild.get_member(member_id) or await guild.fetch_member(member_id)
    
    async def getch_role(self, guild_id: int, role_id: int) -> discord.Role | None:
        guild = await self.getch_guild(guild_id)
        if (role:=guild.get_role(role_id)):
            return role
        role = [role for role in guild.roles if role.id==0]
        if role:
            return role[0]
        
    async def fetch_message(self, channel_id: int, message_id: int) -> discord.Message: 
        channel = await self.getch_channel(channel_id)
        return await channel.fetch_message(message_id)
        