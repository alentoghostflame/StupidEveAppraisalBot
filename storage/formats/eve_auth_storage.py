from storage.formats.config_storage import ConfigData
from pathlib import Path
import urllib.parse
import requests
import logging
import typing
import base64
import yaml
# import os


logger = logging.getLogger("Main")


class EVEAuthStorage:
    def __init__(self, config: ConfigData):
        self.config = config
        self.refresh_token: str = ""

    def from_dict(self, state: dict):
        self.refresh_token = state.get("refresh_token", "")

    def to_dict(self) -> dict:
        return {"refresh_token": self.refresh_token}

    def load(self):
        if Path("{}/cache/eve_auth.yaml".format(self.config.data_folder)).is_file():
            logger.debug("Starting load from cache.")
            file = open("{}/cache/eve_auth.yaml".format(self.config.data_folder), "r")
            raw_data = yaml.safe_load(file)
            file.close()
            self.from_dict(raw_data)
            logger.debug("Finished load from cache.")
        else:
            self.create_refresh_token_guide()

    def save(self):
        logger.debug("Starting save to cache.")
        file = open("{}/cache/eve_auth.yaml".format(self.config.data_folder), "w")
        yaml.safe_dump(self.to_dict(), file)
        file.close()
        logger.debug("Finished save to cache.")

    def create_refresh_token_guide(self):
        if not self.config.eve_app_auth_code and self.create_eve_auth_url_checks():
            self.create_eve_auth_url()
        elif self.config.eve_app_auth_code and not self.refresh_token:
            self.create_refresh_token()

    def create_eve_auth_url_checks(self) -> bool:
        passed_checks = True
        if not self.config.eve_app_client_id:
            logger.error("Missing EVE App client ID in config.")
            passed_checks = False
        if not self.config.eve_app_callback_url:
            logger.error("Missing EVE App callback URL in config.")
            passed_checks = False
        if not self.config.eve_app_scopes:
            logger.error("Missing EVE App scopes in config.")
            passed_checks = False
        if not self.config.eve_app_unique_state:
            logger.error(
                "Missing EVE App unique state. You're supposed to replace the default with something unique, not"
                " remove it.")
            passed_checks = False

        if not passed_checks:
            logger.error("Cannot create EVE App authorization URL, missing components.")
        return passed_checks

    def create_eve_auth_url(self):
        base_url = "https://login.eveonline.com/oauth/authorize/?response_type=code&redirect_uri={}&client_id={}" \
                   "&scope={}&state={}"
        redirect_uri = urllib.parse.quote_plus(self.config.eve_app_callback_url)
        client_id = urllib.parse.quote_plus(self.config.eve_app_client_id)
        scope = urllib.parse.quote_plus(self.config.eve_app_scopes)
        state = urllib.parse.quote_plus(self.config.eve_app_unique_state)

        auth_url = base_url.format(redirect_uri, client_id, scope, state)
        logger.info("Authorization URL: {}\nGo to that website, and authorize your account. You will get redirected"
                    " to the callback_url (which may result in a 404), but what you want is the access code in the"
                    " URL. Look for \"?code=<code here>\" and paste that code in eve_app_access_code in the config."
                    "".format(auth_url))

    def create_refresh_token(self):
        response_dict = self.fetch_refresh_token()
        if response_dict.get("error", "") == "invalid_request":
            logger.error("Failed to get access token: {}".format(response_dict.get("error_description",
                                                                                   "No description found??")))
        elif response_dict.get("refresh_token", ""):
            self.refresh_token = response_dict["refresh_token"]
            logger.info("Received refresh token.")
            self.save()
        else:
            logger.critical("Unexpected response given:\n{}".format(response_dict))

    def fetch_refresh_token(self) -> typing.Optional[dict]:
        auth_key = base64.b64encode(bytes("{}:{}".format(self.config.eve_app_client_id,
                                                         self.config.eve_app_secret_key), "utf-8")).decode("utf-8")
        headers = {"Authorization": "Basic {}".format(auth_key), "Content-Type": "application/x-www-form-urlencoded",
                   "Host": "login.eveonline.com"}
        data_bits = {"grant_type": "authorization_code", "code": self.config.eve_app_auth_code}
        response = requests.post(url="https://login.eveonline.com/oauth/token", headers=headers, data=data_bits)
        return response.json()

    def get_access_token(self) -> typing.Optional[str]:
        if self.refresh_token:
            auth_key = base64.b64encode(bytes("{}:{}".format(self.config.eve_app_client_id,
                                                             self.config.eve_app_secret_key), "utf-8")).decode("utf-8")
            headers = {"Authorization": "Basic {}".format(auth_key),
                       "Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com"}
            data_bits = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
            response = requests.post(url="https://login.eveonline.com/oauth/token", headers=headers, data=data_bits)
            return response.json().get("access_token", None)
        else:
            return None
