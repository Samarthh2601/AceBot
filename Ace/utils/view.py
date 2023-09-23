from discord import ui
import discord


class BookmarkView(ui.View):
    def __init__(self, embed: discord.Embed, *, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embed = embed
        self.timeout = timeout

    @ui.button(label="Copy", style=discord.ButtonStyle.green)
    async def recopy(self, inter: discord.Interaction, button: ui.Button) -> None:
        await inter.response.defer(ephemeral=True, thinking=True)
        try:
            await inter.user.send(embed=self.embed)
            await inter.edit_original_response(content="Successfully replicated the message to your DMs!")
        except discord.Forbidden:
            await inter.edit_original_response(content="Your DMs are disabled! Enable your DMs and click me again!")