import discord
from discord import app_commands
from discord.ext import commands
import pykawaii

from ..core import Ace
from ..utils import Embed


class GIFs(commands.GroupCog, name="gifs"):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot
        self._anime = pykawaii.Client().sfw

    @app_commands.choices(choice=[app_commands.Choice(name=action.capitalize(), value=action) for action in ["handhold", "hug", "smile", "kill", "kick", "slap", "kiss", "cuddle", "bite", "bonk", "cringe", "cry", "happy", "dance", "wave", "highfive", "pat","blush", "lick", "waifu", "megumin", "smug", "nom", "wink", "poke"]])
    @app_commands.command(name="anime")
    async def anime(self, inter: discord.Interaction, choice: str) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        embed = Embed(title=choice.capitalize()).set_image(await (self._anime.__getattribute__(choice)()))
        await inter.edit_original_response(embed=embed)


async def setup(bot: Ace) -> None:
    await bot.add_cog(GIFs(bot))