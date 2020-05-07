from storage import ConfigData
from pathlib import Path
import logging
import typing
import yaml


logger = logging.getLogger("Main")


class AlreadyRegisteredName(Exception):
    """Raised when a cache is already registered under that name."""
    pass


class BaseCache:
    def __init__(self, config: ConfigData, file_name: str):
        self._config = config
        self._file_name = file_name
        self._loaded: bool = False

    def loaded(self) -> bool:
        return self._loaded

    def save(self):
        cache_location = "{}/cache/{}".format(self._config.data_folder, self._file_name)
        file = open(cache_location, "w")
        yaml.safe_dump(self.to_dict(), file)
        file.close()

    def load(self):
        cache_location = "{}/cache/{}".format(self._config.data_folder, self._file_name)
        if Path(cache_location).is_file():
            file = open(cache_location, "r")
            state = yaml.safe_load(file)
            file.close()
            for key in state:
                self.__dict__[key] = state[key]
            self._loaded = True

    def to_dict(self) -> dict:
        output_dict = dict()
        for key in self.__dict__:
            if key[0] != "_":
                output_dict[key] = self.__dict__[key]
        return output_dict


class CacheManager:
    def __init__(self):
        self._caches: typing.Dict[str, BaseCache] = dict()

    def register_cache(self, cache: BaseCache, cache_name: str):
        if cache_name in self._caches:
            raise AlreadyRegisteredName()
        else:
            self._caches[cache_name] = cache

    def get_cache(self, cache_name: str) -> typing.Optional[BaseCache]:
        return self._caches.get(cache_name, None)

    def save(self):
        for cache in self._caches:
            self._caches[cache].save()

    def load(self):
        for cache in self._caches:
            self._caches[cache].load()
