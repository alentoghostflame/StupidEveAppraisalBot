import logging
# import typing
import yaml
import os


logger = logging.getLogger("Main")


class ConfigData:
    def __init__(self):
        self.discord_token: str = ""

        self.sde_folder_name: str = "sde"
        self.data_folder: str = "data"

        self.eve_app_client_id: str = ""
        self.eve_app_secret_key: str = ""
        self.eve_app_callback_url: str = ""
        self.eve_app_scopes: str = ""
        self.eve_app_unique_state: str = "notauniquestate"

        self.eve_app_auth_code: str = ""

    def from_dict(self, state: dict):
        self.discord_token = state.get("discord_token", "")

        self.sde_folder_name = state.get("sde_folder_name", "sde")
        self.data_folder = state.get("data_folder", "data")

        self.eve_app_client_id = state.get("eve_app_client_id", "")
        self.eve_app_secret_key = state.get("eve_app_secret_key", "")
        self.eve_app_callback_url = state.get("eve_app_callback_url", "")
        self.eve_app_scopes = state.get("eve_app_scopes", "")
        self.eve_app_unique_state = state.get("eve_app_unique_state", "notauniquestate")

        self.eve_app_auth_code = state.get("eve_app_auth_code", "")

    def to_dict(self):
        return self.__dict__

    def load(self, file_name: str = "config.yaml"):
        if os.path.exists(file_name):
            file = open(file_name, "r")
            self.load_from(file)
            file.close()
        else:
            logger.warning("Config doesn't exist, creating initial config.")
            file = open(file_name, "w")
            yaml.safe_dump(self.to_dict(), file)
            file.close()
            logger.warning("Initial config created.")

    def load_from(self, file):
        logger.info("Loading config from file \"{}\"".format(file.name))
        temp_dict = yaml.safe_load(file)
        self.from_dict(temp_dict)
        logger.info("Config loaded.")
