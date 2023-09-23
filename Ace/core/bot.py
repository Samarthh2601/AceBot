import asyncio
import aiohttp
import discord
from discord.ext import commands

from ..utils import Info
from .ext import BotSetup, CustomFeatures

class Ace(commands.Bot):
    def __init__(self) -> None:
        super().__init__(Info.COMMANDS_PREFIX, intents=discord.Intents.all(), owner_ids=Info.OWNER_IDS)
        self._bot_setup = BotSetup(self)
        self.features = CustomFeatures(self)
    
    async def _bot_prep(self, token: str) -> None:
        async with aiohttp.ClientSession() as session:
            self.http_client = session
            await self.start(token)

    def run(self) -> None:
        asyncio.run(self._bot_prep(Info.TOKEN))
        
    async def setup_hook(self) -> None:
        self.db = await self._bot_setup.initialize_db()
        self._bot_setup.logger.info("Loaded Extensions from: %s", Info.EXTENSIONS_PATH)
        await self.features.load_extensions_from(Info.EXTENSIONS_PATH)
        await self._bot_setup._tree_setup(Info.APP_COMMANDS_GUILD)
    
    async def on_ready(self) -> None:
        self._bot_setup.load_info()