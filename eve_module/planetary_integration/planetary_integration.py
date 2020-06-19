from eve_module.planetary_integration.pi_control import pi_control
from eve_module.storage import EVEUserAuthManager, ESIUnauthorized
from discord.ext import commands, tasks
from alento_bot import StorageManager
import logging
import aiohttp
import asyncio


logger = logging.getLogger("main_bot")


class EVEPlanetaryIntegrationCog(commands.Cog, name="EVEPI"):
    def __init__(self, storage: StorageManager, user_auth: EVEUserAuthManager):
        self.storage: StorageManager = storage
        self.user_auth: EVEUserAuthManager = user_auth
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.session.close())

    @commands.command(name="pi_control", aliases=["pi", ])
    async def pi_control_command(self, context: commands.Context, arg1=None, arg2=None):
        await pi_control(self.user_auth, self.session, context, arg1, arg2)
