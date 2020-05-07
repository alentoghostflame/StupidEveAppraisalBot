from storage_module.formats import ConfigData, EVEAuthStorage
from storage_module.controllers import CacheManager, BaseCache
import logging
# import typing
from pathlib import Path


logger = logging.getLogger("Main")


class DiskManager:
    def __init__(self):
        self.config: ConfigData = ConfigData()
        # self.cache: CacheManager = CacheManager()
        self.eve_auth: EVEAuthStorage = EVEAuthStorage(self.config)

    def load(self):
        self.config.load()
        # self.cache.load()
        self.eve_auth.load()
        self.create_data_folders()

    def save(self):
        # self.cache.save()
        pass

    def create_data_folders(self):
        base_folder = self.config.data_folder
        Path(base_folder).mkdir(exist_ok=True)
        Path("{}/cache".format(base_folder)).mkdir(exist_ok=True)
