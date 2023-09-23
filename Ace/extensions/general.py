import discord
from discord import app_commands
from discord.ext import commands

from ..core import Ace
from ..utils import Embed


class General(commands.GroupCog, name="general"):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot
    
    @app_commands.command(name="ping", description="Get my ping")
    async def ping(self, inter: discord.Interaction) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        embed = Embed(title="My Latency", description=f"{round(self.bot.latency*1000)}ms")
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="uptime", description="Get my uptime")
    async def uptime(self, inter: discord.Interaction) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        _uptime = self.bot._bot_setup.uptime
        embed = Embed(title="Uptime", description=f"Days: {_uptime.days}\nHours: {_uptime.hours}\nMinutes: {_uptime.minutes}\nSeconds: {_uptime.seconds}")
        await inter.edit_original_response(embed=embed)
    
    
async def setup(bot: Ace) -> None:
    await bot.add_cog(General(bot))