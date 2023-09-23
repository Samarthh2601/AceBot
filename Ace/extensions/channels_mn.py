from discord.ext import commands
from discord import app_commands
import discord

from ..core import Ace
from ..utils import Embed


class ChannelsManager(commands.GroupCog, name="channel"):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.choices(channel_type=[app_commands.Choice(name="Welcome", value="welcome"), app_commands.Choice(name="Member Leave", value="leave"), app_commands.Choice(name="Logs", value="log"), app_commands.Choice(name="Vent", value="vent")])
    @app_commands.command(name="configure", description="Configure a channel")
    async def configure(self, inter: discord.Interaction, channel_type: str, channel: discord.TextChannel) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        channels = await self.bot.db.channels.create(inter.guild.id)
        channels.__setattr__(channel_type, channel.id)
        await self.bot.db.channels.update(inter.guild.id, channels.welcome, channels.leave, channels.log, channels.vent)
        embed = Embed(description=f"Successfully configured channel for **{channel_type}**: {channel.mention}")
        await inter.edit_original_response(embed=embed)

    @app_commands.command(name="view_configuration", description="View the channels configured for the server")    
    async def view_configuration(self, inter: discord.Interaction) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        channels = await self.bot.db.channels.create(inter.guild.id)
        
        embed = Embed(title=f"Channel Configurations for {inter.guild.name}", description=f"**Welcome**: {f'<#{channels.welcome}>' if channels.welcome != 0 else 'No channel configured'}\n**Leave**: {f'<#{channels.leave}>' if channels.leave != 0 else 'No channel configured'}\n**Log**: {f'<#{channels.log}>' if channels.log != 0 else 'No channel configured'}\n**Vent**: {f'<#{channels.vent}>' if channels.vent != 0 else 'No channel configured'}")

        await inter.edit_original_response(embed=embed)

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.choices(channel_type=[app_commands.Choice(name="Welcome", value="welcome"), app_commands.Choice(name="Member Leave", value="leave"), app_commands.Choice(name="Logs", value="log"), app_commands.Choice(name="Vent", value="vent")])
    @app_commands.command(name="reset_configuration", description="Reset a configured channel")
    async def reset_configuration(self, inter: discord.Interaction, channel_type: str) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        channels = await self.bot.db.channels.create(inter.guild.id)
        channels.__setattr__(channel_type, 0)
        await self.bot.db.channels.update(inter.guild.id, channels.welcome, channels.leave, channels.log, channels.vent)
        embed = Embed(description=f"Successfully removed configured channel for **{channel_type}**")
        await inter.edit_original_response(embed=embed)    

async def setup(bot: Ace) -> None:
    await bot.add_cog(ChannelsManager(bot))