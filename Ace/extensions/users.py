from discord.ext import commands
from discord import app_commands
import discord

from ..core import Ace
from ..utils import Embed, generate_timestamp

class Users(commands.GroupCog, name="user"):
    def __init__(self, bot: Ace) -> None:
        self.bot = bot
    
    def get_guild_rank(guild_data: list, member: discord.Member) -> None | int:
        s = sorted(guild_data, key=lambda element: element[2])
        form = list(reversed([record[0] for record in s]))
        return None if form is None else (form.index(member.id) + 1)
    
    @app_commands.command(name="get_avatar", description="Get the avatar of a user")
    async def get_avatar(self, inter: discord.Interaction, user: discord.User=None) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        user = user or inter.user
        embed = Embed().set_image(user.display_avatar.url)
        await inter.edit_original_response(embed=embed)
    
    @app_commands.command(name="info", description="Get the info of a user")
    async def info(self, inter: discord.Interaction, user: discord.User | discord.Member=None) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        user = user or inter.user
        
        embed = Embed(colour=user.top_role.colour).set_thumbnail(user.display_avatar.url)
        
        embed.add_field("Username", user, inline=True).add_field("Display name", user.global_name, inline=True).add_field("Discord ID", user.id).add_field("Status", user.status, inline=True).add_field("Avatar URL", f"[{user.name}'s avatar URL]({user.display_avatar.url})", inline=True)

        embed.add_field("Nickname", user.display_name, inline=True).add_field("Colour", user.top_role.colour, inline=True).add_field("Number of Roles", len(user.roles)-1, inline=True).add_field("Server join", generate_timestamp(user.joined_at), inline=True).add_field("Account created", generate_timestamp(user.created_at), inline=True) if isinstance(user, discord.Member) else ...
        
        embed.add_field("Activity", ", ".join([activity.name for activity in user.activities])) if user.activities else ...

        await inter.edit_original_response(embed=embed)
    
    @app_commands.command(name="rank", description="Display the rank of the member in the current server")
    async def rank(self, inter: discord.Interaction, member: discord.Member=None) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        member = member or inter.user
        user_record = await self.bot.db.ranks.create(inter.user.id, inter.guild.id)
        guild_records = await self.bot.db.ranks._raw_guild_records(inter.guild.id)
        guild_rank = await self.get_guild_rank(guild_records, inter.user)
        
        embed = Embed(title=f"{inter.user.name}'s experience!").set_thumbnail(inter.user.display_avatar.url).add_field("Experience", user_record.experience).add_field("Level", user_record.level).add_field("Rank", guild_rank)
        await inter.edit_original_response(embed=embed)

async def setup(bot: Ace) -> None:
    await bot.add_cog(Users(bot))