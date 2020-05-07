from storage_module.formats import UniverseStorage, ConfigData, ItemStorage
import logging
import os


logger = logging.getLogger("Main")


class SDEManager:
    def __init__(self, config: ConfigData):
        self.config: ConfigData = config
        self.loaded: bool = False
        self.universe: UniverseStorage = UniverseStorage(self.config)
        self.items: ItemStorage = ItemStorage(self.config)

    def load(self):
        if os.path.isdir(self.config.sde_folder_name):
            self.items.load()
            self.loaded = True
        else:
            logger.warning("\"{}\", the path for the SDE folder, is not found!")
