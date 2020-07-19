from eve_module.storage import EVEUserAuthManager, PlanetIntManager
from evelib import EVEManager
from eve_module.planetary_integration.pi_control import pi_control
from eve_module.planetary_integration import text
from discord.ext import commands
import logging
from aiohttp.client_exceptions import ClientOSError


logger = logging.getLogger("main_bot")


class EVEPlanetaryIntegrationCog(commands.Cog, name="EVEPI"):
    def __init__(self, user_auth: EVEUserAuthManager, eve_manager: EVEManager, planet_int: PlanetIntManager):
        self.user_auth: EVEUserAuthManager = user_auth
        self.eve_manager: EVEManager = eve_manager
        self.planet_int = planet_int

    @commands.command(name="pi_control", aliases=["pi", ])
    async def pi_control_command(self, context: commands.Context, arg1=None, arg2=None):
        await pi_control(self.user_auth, self.planet_int, context, arg1, arg2)

    @pi_control_command.error
    async def on_command_error(self, context: commands.Context, error: Exception):
        if isinstance(error, ClientOSError):
            await context.send(text.PI_CONTROL_ERROR_CLIENTOSERROR)
        else:
            await context.send(f"A critical error occurred: {type(error)}: {error}\nSEND THIS TO ALENTO/SOMBRA "
                               f"GHOSTFLAME!")
            raise error
