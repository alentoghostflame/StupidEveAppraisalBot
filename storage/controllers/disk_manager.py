import storage.formats.config_storage
import logging
# import typing
from pathlib import Path


logger = logging.getLogger("Main")


class DiskManager:
    def __init__(self):
        self.config = storage.formats.config_storage.ConfigData()

    def load(self):
        self.config.load()
        self.create_data_folders()

    def create_data_folders(self):
        base_folder = self.config.data_folder
        Path(base_folder).mkdir(exist_ok=True)
        Path("{}/cache".format(base_folder)).mkdir(exist_ok=True)
