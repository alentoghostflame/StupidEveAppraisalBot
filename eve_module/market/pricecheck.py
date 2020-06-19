# from alento_bot import StorageManager
from eve_module.storage import UniverseStorage, ItemStorage, RegionData, ConstellationData, SolarSystemData, ItemData, \
    MarketManager
from eve_module.market import text
from discord.ext import commands
import discord
import logging
import typing


logger = logging.getLogger("main_bot")


async def pricecheck(universe: UniverseStorage, items: ItemStorage, market: MarketManager, context: commands.Context,
                     *args):
    # location_data = None
    # item_data = None
    location_data = None
    args_in_name = 0
    item_data = None

    # location_data = None
    # name_arg_counter = 1
    # for i in range(len(args)):
    #     location_data = universe.get_any(" ".join(args[:i]))
    #     name_arg_counter += 1
    if args:
        location_data, args_in_name = get_location_data_from_list(universe, args)
        if location_data and args[args_in_name:]:
            # logger.debug(f"LOCATION {location_data}, \"{args[args_in_name:]}\", {args}")
            item_data = items.get_item(" ".join(args[args_in_name:]))

    # logger.debug(f"ITEM {item_data}, ARG NAME COUNT {args_in_name}, ARGS {args}")

    if not args:
        await context.send(text.PRICECHECK_HELP)
    elif not location_data:
        await context.send("Location not found in universe.")
    elif not args[args_in_name:]:
        await context.send(f"{location_data.id} : {location_data.name}")
    elif not item_data:
        await context.send("Item not found in database.")
    else:
        if isinstance(location_data, RegionData):
            buy_orders, sell_orders = market.get_item_orders(location_data.id, item_data.id)
            embed = create_embed(buy_orders, sell_orders, item_data, location_data)
            await context.send(embed=embed)
        elif isinstance(location_data, ConstellationData):
            await context.send(text.PRICECHECK_CONSTELLATIONS)
        elif isinstance(location_data, SolarSystemData):
            # region_data = universe.get_region(location_data.region)
            region_data = universe.get_region(location_data.region, is_id=True)
            buy_orders, sell_orders = market.get_item_orders(region_data.id, item_data.id, location_data.id)
            embed = create_embed(buy_orders, sell_orders, item_data, location_data)
            await context.send(embed=embed)
        else:
            await context.send("PRICECHECK.PY/PRICECHECK, DM TO ALENTO/SOMBRA \"{}\"".format(type(location_data)))

    # if arg1:
    #     location_data = universe.get_any(arg1)
    # if args:
    #     item_data = items.get_item(" ".join(args))
    #
    # if not arg1:
    #     await context.send(text.PRICECHECK_HELP)
    # elif not location_data:
    #     await context.send("Location not found in universe.")
    # elif not args:
    #     await context.send("{} : {}".format(location_data.id, location_data.name))
    # elif not item_data:
    #     await context.send("Item not found in database.")
    # else:
    #     if isinstance(location_data, RegionData):
    #         buy_orders, sell_orders = market.get_item_orders(location_data.id, item_data.id)
    #         embed = create_embed(buy_orders, sell_orders, item_data, location_data)
    #         await context.send(embed=embed)
    #     elif isinstance(location_data, ConstellationData):
    #         await context.send(text.PRICECHECK_CONSTELLATIONS)
    #     elif isinstance(location_data, SolarSystemData):
    #         # region_data = universe.get_region(location_data.region)
    #         region_data = universe.get_region(location_data.region, is_id=True)
    #         buy_orders, sell_orders = market.get_item_orders(region_data.id, item_data.id, location_data.id)
    #         embed = create_embed(buy_orders, sell_orders, item_data, location_data)
    #         await context.send(embed=embed)
    #     else:
    #         await context.send("PRICECHECK.PY/PRICECHECK, DM TO ALENTO/SOMBRA \"{}\"".format(type(location_data)))


def get_location_data_from_list(universe: UniverseStorage, string_list: typing.Tuple[str, ...]):
    name_arg_counter = 0
    for i in range(len(string_list)):
        name_arg_counter += 1
        logger.debug(f"Trying {' '.join(string_list[:i + 1])}, count {name_arg_counter}")
        location_data = universe.get_any(" ".join(string_list[:i + 1]))
        if location_data:
            logger.debug(f"Found {' '.join(string_list[:i + 1])}")
            return location_data, name_arg_counter
    return None, 0


def create_embed(buy_orders: typing.List[dict], sell_orders: typing.List[dict], item_data: ItemData, location_data):
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
