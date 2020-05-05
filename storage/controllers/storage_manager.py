import storage.controllers.disk_manager
import storage.controllers.sde_manager
import logging


logger = logging.getLogger("Main")


class StorageManager:
    def __init__(self):
        self.disk = storage.controllers.disk_manager.DiskManager()
        self.sde = storage.controllers.sde_manager.SDEManager(self.disk.config)

    def load(self):
        self.disk.load()
        self.sde.load()
