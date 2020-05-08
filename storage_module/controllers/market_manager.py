from storage_module.controllers.cache_manager import CacheManager, BaseCache
from storage_module.controllers.eve_auth_manager import EVEAuthManager
from storage_module.formats.config_storage import ConfigData
import requests
import logging
import typing


logger = logging.getLogger("Main")


class MarketManager:
    def __init__(self, config: ConfigData, cache_manager: CacheManager, auth: EVEAuthManager):
        self.config: ConfigData = config
        self.cache = MarketCache(self.config)
        cache_manager.register_cache(self.cache, "market_cache")
        self.auth: EVEAuthManager = auth
        self.structure_market_data: typing.Dict[int, typing.List[dict]] = dict()

    def get_item_orders(self, region_id: int, item_id: int, solar_system_id: int = None) -> \
            typing.Tuple[typing.List[dict], typing.List[dict]]:
        raw_market_data = fetch_npc_market_data(region_id, item_id)
        bypass_list = list()
        if solar_system_id:
            # print(self.get_all_structure_item_orders(solar_system_id, item_id))
            bypass_list.extend(self.get_all_structure_item_orders(solar_system_id, item_id))
        return sort_market_data(raw_market_data, solar_system_id, system_bypass_list=bypass_list)

    def get_structure_item_orders(self, structure_id: int, item_id: int) -> typing.List[dict]:
        filtered_orders = list()
        for order in self.structure_market_data.get(structure_id, list()):
            if order.get("type_id", 0) == item_id:
                filtered_orders.append(order)
        return filtered_orders

    def get_all_structure_item_orders(self, solar_system_id: int, item_id: int):
        struct_ids = list()
        for tracked_struct_id in self.cache.tracked_structure_data:
            if self.cache.tracked_structure_data[tracked_struct_id]["solar_system_id"] == solar_system_id:
                struct_ids.append(tracked_struct_id)

        filtered_market_orders = list()
        for struct_id in struct_ids:
            filtered_orders = self.get_structure_item_orders(struct_id, item_id)
            filtered_market_orders.extend(filtered_orders)
        return filtered_market_orders

    def refresh_structure_info(self):
        for structure_id in self.cache.tracked_structures:
            raw_data = self.get_structure_info(structure_id)
            self.cache.tracked_structure_data[structure_id] = {"solar_system_id": raw_data.get("solar_system_id", 0),
                                                               "name": raw_data.get("name", "ERROR FORBIDDEN.")}

    def get_structure_info(self, structure_id: int) -> dict:
        base_url = "https://esi.evetech.net/latest/universe/structures/{}/"
        token = self.auth.get_access_token()
        raw_data = requests.get(url=base_url.format(structure_id), params={"token": token})
        return raw_data.json()

    def refresh_structure_market_orders(self):
        for structure_id in self.cache.tracked_structure_data:
            raw_market_data = self.fetch_structure_market_data(structure_id)
            self.structure_market_data[structure_id] = raw_market_data

    def fetch_structure_market_data(self, structure_id: int) -> typing.List[dict]:
        token = self.auth.get_access_token()
        base_url = "https://esi.evetech.net/latest/markets/structures/{}/"
        raw_market_data = requests.get(base_url.format(structure_id), params={"token": token, })
        return raw_market_data.json()


def fetch_npc_market_data(region_id: int, item_id: int) -> typing.List[dict]:
    base_url = "https://esi.evetech.net/latest/markets/{}/orders"
    return requests.get(url=base_url.format(region_id), params={"type_id": item_id}).json()


def sort_market_data(raw_market_data: typing.List[dict], system_id: int = None, system_bypass_list: list = list()):
    trimmed_list = list()
    if system_id:
        for market_order in raw_market_data:
            if market_order.get("system_id", 0) == system_id:
                trimmed_list.append(market_order)

    else:
        trimmed_list = raw_market_data

    trimmed_list.extend(system_bypass_list)

    buy_orders = list()
    sell_orders = list()
    for order_dict in trimmed_list:
        if order_dict["is_buy_order"]:
            buy_orders.append(order_dict)
        else:
            sell_orders.append(order_dict)

    buy_orders = sorted(buy_orders, key=lambda k: k["price"], reverse=True)
    sell_orders = sorted(sell_orders, key=lambda k: k["price"])
    return buy_orders, sell_orders


class MarketCache(BaseCache):
    def __init__(self, config):
        super().__init__(config, "market_data.yaml")
        self.tracked_structures = [1033152401278, ]
        self.tracked_structure_data: dict = {}
