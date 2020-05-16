from alento_bot import StorageManager, DiscordBot
from eve_module.storage import EVEAuthManager, EVEConfig, UniverseStorage, ItemStorage, MarketManager
from eve_module.misc import EVEMiscCog
from eve_module.market import EVEMarketCog
import logging


logger = logging.getLogger("main_bot")


class EVEModule:
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage
        # noinspection PyArgumentList
        self.eve_config: EVEConfig = EVEConfig(self.storage.config)
        self.storage.caches.register_cache(self.eve_config, "eve_config")
        self.universe: UniverseStorage = UniverseStorage(self.storage)
        self.auth: EVEAuthManager = EVEAuthManager(storage)
        self.items: ItemStorage = ItemStorage(self.storage)
        self.market = MarketManager(self.eve_config, self.auth)

    def register_cogs(self, discord_bot: DiscordBot):
        logger.info("Registering cogs for EVE")
        discord_bot.add_cog(EVEMiscCog())
        discord_bot.add_cog(EVEMarketCog(self.storage, self.universe, self.items, self.market))

    def load(self):
        self.auth.load()
        self.items.load()
