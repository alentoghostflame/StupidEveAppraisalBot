from storage_module.formats.config_storage import ConfigData
from pathlib import Path
import logging
import typing
import yaml


logger = logging.getLogger("Main")


class ItemData:
    def __init__(self, item_id: int = 0, state: dict = None, sde=False):
        self.id: int = item_id

        # self.group_id: int = 0
        # self.mass: int = 0
        self.name: str = ""
        # self.volume: int = 0

        if state and sde:
            self.from_sde_dict(state)
        elif state and not sde:
            self.from_dict(state)

    def from_sde_dict(self, state: dict):
        state_id = state.get("id", 0)
        if state_id:
            self.id = state_id
        # self.group_id = state.get("groupID", 0)
        # self.mass = state.get("mass", 0)
        self.name = state.get("name", dict()).get("en", "")
        # self.volume = state.get("volume", 0)

    def from_dict(self, state: dict):
        self.id = state.get("id", 0)
        # self.group_id = state.get("groupID", 0)
        # self.mass = state.get("mass", 0)
        self.name = state.get("name", "")
        # self.volume = state.get("volume", 0)

    def to_dict(self):
        return self.__dict__


class ItemStorage:
    def __init__(self, config: ConfigData):
        self._config: ConfigData = config
        self.items: typing.Dict[str, ItemData] = dict()

    def load(self):
        if Path("{}/cache/items.yaml".format(self._config.data_folder)).is_file():
            self.load_from_cache()
        else:
            self.load_from_sde()
            self.save_to_cache()

    def load_from_cache(self):
        logger.debug("Starting load from cache.")
        file = open("{}/cache/items.yaml".format(self._config.data_folder), "r")
        raw_data = yaml.safe_load(file)
        file.close()
        for item_name in raw_data:
            self.items[item_name] = ItemData(state=raw_data[item_name])
        logger.debug("Finished load from cache.")

    def load_from_sde(self):
        logger.debug("Starting load from SDE. (May take some time)")
        base_folder = "{}/fsd".format(self._config.sde_folder_name)
        item_file = open("{}/typeIDs.yaml".format(base_folder))
        raw_data = yaml.safe_load(item_file)
        item_file.close()

        for item_id in raw_data:

            item_data = ItemData(item_id, raw_data[item_id], sde=True)
            self.items[item_data.name.lower()] = item_data
        logger.debug("Finished load from SDE.")

    def save_to_cache(self):
        logger.debug("Starting save to cache.")
        disk_dict: typing.Dict[str, dict] = dict()
        for item_name in self.items:
            disk_dict[item_name.lower()] = self.items[item_name.lower()].to_dict()
        file = open("{}/cache/items.yaml".format(self._config.data_folder), "w")
        yaml.safe_dump(disk_dict, file)
        file.close()
        logger.debug("Finished save to cache.")

    def get_item(self, item_name: str) -> typing.Optional[ItemData]:
        return self.items.get(item_name.lower(), None)




