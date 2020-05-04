import storage.controllers.disk_manager
import logging


logger = logging.getLogger("Main")


class StorageManager:
    def __init__(self):
        self.disk = storage.controllers.disk_manager.DiskManager()

    def load(self):
        self.disk.load()
