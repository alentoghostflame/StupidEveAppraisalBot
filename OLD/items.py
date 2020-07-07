from alento_bot import StorageManager, ConfigData, cache_transformer
from eve_module.storage.eve_config import EVEConfig
from pathlib import Path
import logging
import typing
import yaml


logger = logging.getLogger("main_bot")


class ItemData:
    def __init__(self, item_id: int = 0, state: dict = None, sde=False):
        self.id: int = item_id
        self.name: str = "Default name."
        if state and sde:
            self.from_sde_dict(state)
        elif state and not sde:
            self.from_dict(state)

    def from_sde_dict(self, state: dict):
        state_id = state.get("id", 0)
        if state_id:
            self.id = state_id
        self.name = state.get("name", dict()).get("en", "Name not found in SDE.")

    def from_dict(self, state: dict):
        self.id = state.get("id", 0)
        self.name = state.get("name", "Name not found in Cache.")

    def to_dict(self) -> dict:
        return self.__dict__


class ItemStorage:
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage
        self.config: ConfigData = storage.config
        self.eve_config: EVEConfig = self.storage.caches.get_cache("eve_config")
        # noinspection PyArgumentList
        self.cache = ItemCache(self.config)
        self.storage.caches.register_cache(self.cache, "eve_item_cache")
        self.items: typing.Dict[str, ItemData] = dict()

    def load(self):
        if Path(f"{self.config.data_folder_path}/cache/eve_item_cache.yaml").is_file():
            self.load_from_cache()
        else:
            self.load_from_sde()
            self.save_to_cache()

    def load_from_cache(self):
        for item_name in self.cache.items:
            self.items[item_name.lower()] = ItemData(state=self.cache.items[item_name])

    def load_from_sde(self):
        logger.debug("Loading items from SDE. (May take some time)")
        item_file_location = f"{self.eve_config.sde_location}/fsd/typeIDs.yaml"
        item_file = open(item_file_location, "r")
        raw_data = yaml.safe_load(item_file)
        item_file.close()

        for item_id in raw_data:
            item_data = ItemData(item_id, raw_data[item_id], True)
            self.items[item_data.name.lower()] = item_data
            self.cache.ids[item_id] = item_data.name.lower()
        logger.debug("Finished loading items from SDE.")

    def save_to_cache(self):
        for item_name in self.items:
            self.cache.items[item_name.lower()] = self.items[item_name].to_dict()
        self.cache.save()

    def get_item(self, item) -> typing.Optional[ItemData]:
        if isinstance(item, str):
            return self.items.get(item.lower(), None)
        elif isinstance(item, int):
            return self.items.get(self.cache.ids.get(item, 0), None)
        else:
            raise NotImplementedError(f"The following type is not implemented in this: {type(item)}")


@cache_transformer(name="eve_item_cache", save_on_exit=False)
class ItemCache:
    def __init__(self):
        self.items: typing.Dict[str, dict] = dict()
        self.ids: typing.Dict[int, str] = dict()
