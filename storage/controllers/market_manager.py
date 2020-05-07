# from storage. import ConfigData, CacheManager, BaseCache, EVEAuthStorage
from storage.controllers.cache_manager import CacheManager, BaseCache
from storage.formats.eve_auth_storage import EVEAuthStorage
from storage.formats.config_storage import ConfigData
import requests
import logging
import typing


logger = logging.getLogger("Main")


class MarketManager:
    def __init__(self, config: ConfigData, cache: CacheManager, auth: EVEAuthStorage):
        self.config: ConfigData = config
        self.cache_manager: CacheManager = cache
        self.cache = MarketCache(self.config)
        self.cache_manager.register_cache(self.cache, "market_cache")
        self.auth: EVEAuthStorage = auth


def get_item_orders(self, region_id: int, item_id: int, solar_system_id: int = None):
    raw_market_data = fetch_market_data(region_id, item_id)
    market_data = sort_market_data(raw_market_data, solar_system_id)


def fetch_market_data(region_id: int, item_id: int) -> typing.List[dict]:
    base_url = "https://esi.evetech.net/latest/markets/{}/orders"
    return requests.get(url=base_url.format(region_id), params={"type_id": item_id}).json()


def sort_market_data(raw_market_data: typing.List[dict], system_id: int = None):
    trimmed_list = list()
    if system_id:
        for market_order in raw_market_data:
            if market_order["system_id"] == system_id:
                trimmed_list.append(market_order)
    else:
        trimmed_list = raw_market_data

    sell_orders = list()
    buy_orders = list()
    for order_dict in trimmed_list:
        if order_dict["is_buy_order"]:
            buy_orders.append(order_dict)
        else:
            sell_orders.append(order_dict)

    sell_orders = sorted(sell_orders, key=lambda k: k["price"])
    buy_orders = sorted(buy_orders, key=lambda k: k["price"], reverse=True)
    return sell_orders, buy_orders


class MarketCache(BaseCache):
    def __init__(self, config):
        super().__init__(config, "market_data.yaml")
        self.test_datapoint = "LOLOLOLOL"
