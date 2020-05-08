from storage_module.formats.config_storage import ConfigData
from storage_module.controllers.cache_manager import CacheManager
from storage_module.controllers.sde_manager import SDEManager
from storage_module.formats.eve_auth_storage import EVEAuthStorage
from storage_module.controllers.market_manager import MarketManager

import logging


logger = logging.getLogger("Main")


class StorageManager:
    def __init__(self):
        self.config: ConfigData = ConfigData()
        # self.disk = storage_module.controllers.disk_manager.DiskManager()
        self.cache: CacheManager = CacheManager()
        self.eve_auth: EVEAuthStorage = EVEAuthStorage(self.config)
        self.sde: SDEManager = SDEManager(self.config)
        self.market: MarketManager = MarketManager(self.config, self.cache, self.eve_auth)

    def load(self):
        self.config.load()
        self.cache.load()
        # self.disk.load()
        self.sde.load()

    def save(self):
        # self.disk.save()
        self.cache.save()
