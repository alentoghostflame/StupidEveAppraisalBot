from eve_module.market import text, pricecheck
from eve_module.storage import UniverseStorage, ItemStorage, MarketManager
from discord.ext import commands, tasks
from alento_bot import StorageManager
import logging


logger = logging.getLogger("main_bot")


class EVEMarketCog(commands.Cog, name="EVEMarket"):
    def __init__(self, storage: StorageManager, universe: UniverseStorage, items: ItemStorage, market: MarketManager):
        self.storage: StorageManager = storage
        self.universe = universe
        self.items = items
        self.market = market

    @commands.command(name="pricecheck", brief=text.PRICECHECK_BRIEF, aliases=["pc", ], usage=text.PRICECHECK_USAGE)
    async def pricecheck_command(self, context: commands.Context, arg1=None, *args):
        await pricecheck.pricecheck(self.storage, self.universe, self.items, self.market, context, arg1, *args)

    async def start_tasks(self):
        self.market_refresh_structure_info.start()
        self.market_refresh_orders.start()

    def cog_unload(self):
        self.market_refresh_structure_info.cancel()
        self.market_refresh_orders.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("Starting EVE Market background task loops.")
        await self.start_tasks()

    @tasks.loop(hours=24)
    async def market_refresh_structure_info(self):
        self.market.refresh_structure_info()

    @tasks.loop(hours=1)
    async def market_refresh_orders(self):
        self.market.refresh_structure_market_orders()
