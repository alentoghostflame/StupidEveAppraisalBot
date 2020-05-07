import storage.controllers.disk_manager
import storage.controllers.sde_manager
from storage.controllers.market_manager import MarketManager
from storage.controllers.cache_manager import CacheManager
import logging


logger = logging.getLogger("Main")


class StorageManager:
    def __init__(self):
        self.disk = storage.controllers.disk_manager.DiskManager()
        self.cache: CacheManager = CacheManager()
        self.sde = storage.controllers.sde_manager.SDEManager(self.disk.config)
        self.market: MarketManager = MarketManager(self.disk.config, self.cache, self.disk.eve_auth)

    def load(self):
        self.disk.load()
        self.sde.load()

    def save(self):
        self.disk.save()
