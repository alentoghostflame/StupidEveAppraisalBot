import logging
import typing
import yaml
import os


logger = logging.getLogger("Main")


class ConfigData:
    def __init__(self):
        self.token: str = ""

    def from_dict(self, state: dict):
        self.token = state.get("token", "")

    def to_dict(self):
        return self.__dict__

    def load(self, file_name: str = "config.yaml"):
        if os.path.exists(file_name):
            file = open(file_name, "r")
            self.load_from(file)
        else:
            logger.warning("Config doesn't exist, creating initial config.")
            file = open(file_name, "w")
            yaml.safe_dump(self.to_dict(), file)
            logger.warning("Initial config created.")

    def load_from(self, file):
        logger.info("Loading config from file \"{}\"".format(file.name))
        temp_dict = yaml.safe_load(file)
        self.from_dict(temp_dict)
        logger.info("Config loaded.")

