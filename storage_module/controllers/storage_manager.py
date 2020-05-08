from storage_module.formats.config_storage import ConfigData
from storage_module.controllers.cache_manager import CacheManager
from storage_module.controllers.sde_manager import SDEManager
from storage_module.controllers.eve_auth_manager import EVEAuthManager
from storage_module.controllers.market_manager import MarketManager

import logging


logger = logging.getLogger("Main")


class StorageManager:
    def __init__(self):
        self.config: ConfigData = ConfigData()
        self.cache: CacheManager = CacheManager()
        self.eve_auth: EVEAuthManager = EVEAuthManager(self.config, self.cache)
        self.sde: SDEManager = SDEManager(self.config)
        self.market: MarketManager = MarketManager(self.config, self.eve_auth)

    def load(self):
        self.config.load()
        self.cache.load()
        self.sde.load()
        self.eve_auth.load()
        self.market.refresh_structure_info()
        self.market.refresh_structure_market_orders()

    def save(self):
        self.cache.save()
