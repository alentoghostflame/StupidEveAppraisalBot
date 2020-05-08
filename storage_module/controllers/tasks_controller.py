from storage_module.controllers.storage_manager import StorageManager
from discord.ext import commands, tasks

import logging


logger = logging.getLogger("Main")


class TasksCog(commands.Cog):
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage

    async def start_tasks(self):
        await self.market_refresh_orders.start()
        await self.market_refresh_structure_info.start()

    def cog_unload(self):
        self.market_refresh_orders.cancel()
        self.market_refresh_structure_info.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("Starting background task loops.")
        await self.start_tasks()

    @tasks.loop(hours=1)
    async def market_refresh_orders(self):
        self.storage.market.refresh_structure_market_orders()

    @tasks.loop(hours=24)
    async def market_refresh_structure_info(self):
        self.storage.market.refresh_structure_info()
