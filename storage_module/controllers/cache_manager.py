from storage_module.formats.config_storage import ConfigData
from pathlib import Path
import logging
import typing
import yaml


logger = logging.getLogger("Main")


class AlreadyRegisteredName(Exception):
    """Raised when a cache is already registered under that name."""
    pass


class BaseCache:
    def __init__(self, config: ConfigData, file_name: str, save_on_exit: bool = True):
        self._config: ConfigData = config
        self._file_name: str = file_name
        self._save_on_exit: bool = save_on_exit
        self._loaded: bool = False

    def loaded(self) -> bool:
        return self._loaded

    def save(self, exiting: bool = False):
        if not exiting or (exiting and self._save_on_exit):
            logger.debug("Saving cache {}".format(self._file_name))
            cache_location = "{}/cache/{}".format(self._config.data_folder, self._file_name)
            file = open(cache_location, "w")
            yaml.safe_dump(self.to_dict(), file)
            file.close()
            logger.debug("Saved {}".format(self._file_name))
        else:
            logger.debug("Cache {} disabled save on exit, ignoring.".format(self._file_name))

    def load(self):
        logger.debug("Loading cache {}".format(self._file_name))
        cache_location = "{}/cache/{}".format(self._config.data_folder, self._file_name)
        if Path(cache_location).is_file():
            file = open(cache_location, "r")
            state = yaml.safe_load(file)
            file.close()
            for key in state:
                self.__dict__[key] = state[key]
            self._loaded = True
            logger.debug("Loaded {}".format(self._file_name))
        else:
            logger.debug("{} not on disk yet.".format(self._file_name))

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
            raise AlreadyRegisteredName("\"{}\" already registered.".format(cache_name))
        else:
            logger.debug("{} registered".format(cache_name))
            self._caches[cache_name] = cache

    def get_cache(self, cache_name: str) -> typing.Optional[BaseCache]:
        return self._caches.get(cache_name, None)

    def save(self):
        logger.info("Saving caches...")
        for cache in self._caches:
            self._caches[cache].save(exiting=True)
        logger.info("Caches saved.")

    def load(self):
        logger.info("Loading caches...")
        for cache in self._caches:
            self._caches[cache].load()
        logger.info("Caches loaded.")
