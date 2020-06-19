from alento_bot import StorageManager
from eve_module.storage import EVEAuthManager, EVEUserAuthManager
from eve_module.user_auth.commands import eve_auth_control
from discord.ext import commands
import logging
# import discord


logger = logging.getLogger("main_bot")


class EVEAuthCog(commands.Cog, name="EVE Auth"):
    def __init__(self, storage: StorageManager, auth: EVEAuthManager, user_auth: EVEUserAuthManager):
        self.storage: StorageManager = storage
        self.auth: EVEAuthManager = auth
        self.user_auth: EVEUserAuthManager = user_auth

    @commands.command(name="eve_auth", aliases=["auth", ])
    async def eve_auth_control_command(self, context: commands.Context, arg1=None, arg2=None):
        await eve_auth_control(self.user_auth, context, arg1, arg2)

    # @commands.command(name="gat")
    # async def debug_get_access_token(self, context: commands.Context):
    #     """
    #     THIS IS DEBUG AND SHOULD BE REMOVED LATER
    #     :param context:
    #     :return:
    #     """
    #     token = self.auth.get_access_token()
    #     await context.send(f"Token: ```{token}```")
