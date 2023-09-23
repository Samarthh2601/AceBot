import discord
from discord import app_commands
from discord.ext import commands

from ..core import Ace
from ..utils import Info, get_all_extension_choices

all_extensions = get_all_extension_choices()

class Admin(commands.GroupCog, name="admin"):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot

    async def cog_check(self, inter: discord.Interaction) -> bool:
        return inter.user in self.bot.owner_ids

    @app_commands.choices(cog=all_extensions)
    @app_commands.command(name="reload",  description="Reload cog(s)")
    async def reload(self, inter: discord.Interaction, cog: str=None) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        if cog is None:
            await self.bot.features.reload_extensions_from(Info.EXTENSIONS_PATH)
        else:
            await self.bot.reload_extension(cog)
        await inter.edit_original_response(content="Successfully reloaded!")

async def setup(bot: Ace) -> None:
    await bot.add_cog(Admin(bot))
