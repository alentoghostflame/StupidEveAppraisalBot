from user_commands.market import text, pricecheck
from discord.ext import commands
from storage import SDEManager
import logging


logger = logging.getLogger("Main")


class MarketCog(commands.Cog, name="Market"):
    def __init__(self, bot: commands.Bot, sde_manager: SDEManager):
        self.bot = bot
        self.sde: SDEManager = sde_manager

    @commands.command(name="pricecheck", brief=text.PRICECHECK_BRIEF, aliases=["pc", ], usage=text.PRICECHECK_USAGE)
    async def pricecheck_command(self, context: commands.Context, arg1=None, *args):
        await pricecheck.pricecheck(self.sde, context, arg1, *args)
