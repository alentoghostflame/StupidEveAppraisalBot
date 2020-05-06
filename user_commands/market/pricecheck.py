from user_commands.market import text
from discord.ext import commands
from storage import SDEManager, ItemData
import requests
import storage
import logging
import discord
import typing


logger = logging.getLogger("Main")


async def pricecheck(sde: SDEManager, context: commands.context, arg1=None, *args):
    location_data = None
    item_data = None

    if arg1:
        location_data = sde.universe.eve.get_any(arg1)
    if args:
        item_data = sde.items.get_item(" ".join(args))

    if not arg1:
        await context.send(text.PRICECHECK_HELP)
    elif not location_data:
        await context.send("Not found in universe.")
    elif not args:
        await context.send("{} : {}".format(location_data.id, location_data.name))
    elif not item_data:
        await context.send("Item not found!")
    else:
        if isinstance(location_data, storage.RegionData):
            raw_market_data = fetch_market_data(location_data.id, item_data.id)
            sell_orders, buy_orders = sort_market_data(raw_market_data)
            embed = create_embed(sell_orders, buy_orders, item_data, location_data)
            await context.send(embed=embed)
        elif isinstance(location_data, storage.ConstellationData):
            await context.send(text.PRICECHECK_CONSTELLATIONS)
        elif isinstance(location_data, storage.SolarSystemData):
            region_data = sde.universe.eve.get_region(location_data.region)
            raw_market_data = fetch_market_data(region_data.id, item_data.id)
            sell_orders, buy_orders = sort_market_data(raw_market_data, location_data.id)
            embed = create_embed(sell_orders, buy_orders, item_data, location_data)
            await context.send(embed=embed)
        else:
            await context.send("PRICECHECK.PY/PRICECHECK, DM TO ALENTO/SOMBRA \"{}\"".format(type(location_data)))


def create_embed(sell_orders: typing.List[dict], buy_orders: typing.List[dict], item_data: ItemData, location_data):
    embed = discord.Embed(title="{}: {}".format(location_data.name, item_data.name), color=0xffff00)

    seller_text = ""
    x = 0
    while x < 5 and x < len(sell_orders):
        seller_text += "{}) {} for {} ISK\n".format(x + 1, human_format(sell_orders[x]["volume_remain"], small_dec=0), human_format(sell_orders[x]["price"]))
        x += 1
    if not seller_text:
        seller_text = "None"
    embed.add_field(name="{} Sell Orders".format(len(sell_orders)), value=seller_text, inline=True)

    buyer_text = ""
    x = 0
    while x < 5 and x < len(buy_orders):
        buyer_text += "{}) {} for {} ISK\n".format(x + 1, human_format(buy_orders[x]["volume_remain"], small_dec=0), human_format(buy_orders[x]["price"]))
        x += 1
    if not buyer_text:
        buyer_text = "None"
    embed.add_field(name="{} Buy Orders".format(len(buy_orders)), value=buyer_text, inline=True)

    if len(sell_orders) > 0:
        if len(buy_orders) > 0 and sell_orders[0]["price"] * 0.9 <= buy_orders[0]["price"]:
            suggestion_text = "Suggested sell price: {} ISK (highest buy price)".format(human_format(buy_orders[0]["price"]))
        else:
            suggestion_text = "Suggested sell price: {} ISK (90% of lowest sell)".format(human_format(sell_orders[0]["price"] * 0.9))
    else:
        suggestion_text = "Not enough data."

    embed.add_field(name="Sell For", value=suggestion_text, inline=False)
    return embed


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


def fetch_market_data(region_id: int, item_id: int) -> typing.List[dict]:
    base_url = "https://esi.evetech.net/latest/markets/{}/orders"
    data = requests.get(url=base_url.format(region_id), params={"type_id": item_id}).json()
    return data
    # return requests.get(url=base_url.format(region_id), params={"type_id": item_id}).json()


def human_format(number: int, dec: int = 2, small_dec: int = 2):
    units = ["", "K", "M", "G", "T", "P"]
    temp_num = number
    magnitude = 0
    while temp_num > 10000 and not (magnitude == 0 and temp_num < 100000):
        temp_num /= 1000
        magnitude += 1
    if magnitude == 0:
        return "{:,.{}f}{}".format(temp_num, small_dec, units[magnitude])
    elif len("{:.0f}".format(temp_num)) > 3:
        return "{:,.0f}{}".format(temp_num, units[magnitude])
    else:
        return "{:,.{}f}{}".format(temp_num, dec, units[magnitude])

