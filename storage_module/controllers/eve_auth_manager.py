from storage_module.formats.config_storage import ConfigData
from storage_module.controllers.cache_manager import CacheManager, BaseCache
# from pathlib import Path
import urllib.parse
import requests
import logging
import typing
import base64
# import yaml
# import os


logger = logging.getLogger("Main")


class EVEAuthManager:
    def __init__(self, config: ConfigData, cache_manager: CacheManager):
        self.config = config
        self.cache: EVEAuthCache = EVEAuthCache(self.config)
        cache_manager.register_cache(self.cache, "eve_auth")
        # self.refresh_token: str = ""

    def load(self):
        if not self.cache.loaded() or not self.cache.refresh_token:
            self.create_refresh_token_guide()

    def create_refresh_token_guide(self):
        if not self.config.eve_app_auth_code and self.create_eve_auth_url_checks():
            self.create_eve_auth_url()
        elif self.config.eve_app_auth_code and not self.cache.refresh_token:
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
                    " URL. Look for \"?code=<code here>\" and paste that code in eve_auth_app_code in the config."
                    "".format(auth_url))

    def create_refresh_token(self):
        response_dict = self.fetch_refresh_token()
        if response_dict.get("error", "") == "invalid_request":
            logger.error("Failed to get access token: {}".format(response_dict.get("error_description",
                                                                                   "No description found??")))
        elif response_dict.get("refresh_token", ""):
            self.cache.refresh_token = response_dict["refresh_token"]
            logger.info("Received refresh token.")
            self.cache.save()
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
        if self.cache.refresh_token:
            auth_key = base64.b64encode(bytes("{}:{}".format(self.config.eve_app_client_id,
                                                             self.config.eve_app_secret_key), "utf-8")).decode("utf-8")
            headers = {"Authorization": "Basic {}".format(auth_key),
                       "Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com"}
            data_bits = {"grant_type": "refresh_token", "refresh_token": self.cache.refresh_token}
            response = requests.post(url="https://login.eveonline.com/oauth/token", headers=headers, data=data_bits)
            return response.json().get("access_token", None)
        else:
            return None


class EVEAuthCache(BaseCache):
    def __init__(self, config: ConfigData):
        super().__init__(config, "eve_auth.yaml")
        self.refresh_token = ""
