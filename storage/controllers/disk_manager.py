import storage.formats.config_storage
import typing


class DiskManager:
    def __init__(self):
        self.config = storage.formats.config_storage.ConfigData()

    def load(self):
        self.config.load()
