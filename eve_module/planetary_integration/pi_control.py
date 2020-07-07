from eve_module.storage import EVEUserAuthManager, PlanetIntManager, FactoryInfo, ExtractorInfo, BasicPinInfo, \
    PlanetPIInfo
from eve_module.planetary_integration import text
from discord.ext import commands
from datetime import datetime, timedelta
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def pi_control(user_auth: EVEUserAuthManager, planet_int: PlanetIntManager, context: commands.Context, arg1: str,
                     arg2: str):
    user_scopes = user_auth.get_selected_scopes(context.author.id)
    if not user_scopes:
        await context.send(text.NO_AUTH_SELECTED_CHARACTER)
    elif not arg1:
        await send_help_embed(context)
    elif arg1 not in {"enable", "disable", "update", "info", "planet"}:
        await context.send(text.PI_CONTROL_MISSING_ARG_1)
    elif user_scopes.get("esi-planets.manage_planets.v1", None) is None:
        await context.send(text.AUTH_SCOPE_MISSING.format("esi-planets.manage_planets.v1"))
    elif arg1 == "enable":
        await enable_pi(user_auth, context)
    elif not user_scopes.get("esi-planets.manage_planets.v1", None):
        await context.send(text.PI_CONTROL_SCOPE_FALSE)
    elif arg1 == "disable":
        await disable_pi(user_auth, context)
    elif arg1 == "update":
        await update_control(user_auth, planet_int, context, arg2)
    elif arg1 == "info":
        await send_info_embed(user_auth, planet_int, context, arg2)
    else:
        await context.send(f"PI_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\". SEND THIS TO ALENTO/SOMBRA GHOSTFLAME!")


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Planetary Interaction", color=0x8CB1DE)

    embed.add_field(name="Description", value=text.PI_CONTROL_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Permissions", value=text.PI_CONTROL_HELP_COMMAND_PERMISSION, inline=False)
    embed.add_field(name="Updating", value=text.PI_CONTROL_HELP_COMMAND_UPDATE, inline=False)
    embed.add_field(name="Information", value=text.PI_CONTROL_HELP_COMMAND_INFORMATION, inline=False)

    await context.send(embed=embed)


async def enable_pi(user_auth: EVEUserAuthManager, context: commands.Context):
    if user_auth.set_selected_desired_scope(context.author.id, "esi-planets.manage_planets.v1", True):
        await context.send(text.PI_CONTROL_ENABLE_SUCCESS)
    else:
        await context.send(text.PI_CONTROL_INVALID_CHAR_OR_PERMISSION)


async def disable_pi(user_auth: EVEUserAuthManager, context: commands.Context):
    if user_auth.set_selected_desired_scope(context.author.id, "esi-planets.manage_planets.v1", False):
        await context.send(text.PI_CONTROL_DISABLE_SUCCESS)
    else:
        await context.send(text.PI_CONTROL_INVALID_CHAR_OR_PERMISSION)


async def update_control(user_auth: EVEUserAuthManager, planet_int: PlanetIntManager, context: commands.Context,
                         arg: str):
    planet_id = get_numbers(arg)
    if not arg:
        await context.send(text.PI_CONTROL_UPDATE_MISSING_ARG)
    elif not planet_id and arg not in {"basic", "full"}:
        await context.send(text.PI_CONTROL_MISSING_ARG_1)
    elif planet_id:
        if await planet_int.update_pi_planet(context.author.id, user_auth.get_selected(context.author.id), planet_id):
            await context.send(text.PI_CONTROL_UPDATE_PLANET_SUCCESS.format(planet_id))
        else:
            await context.send(text.PI_CONTROL_UPDATE_PLANET_NOT_FOUND)
    elif arg == "basic":
        await planet_int.update_pi_info(context.author.id, user_auth.get_selected(context.author.id))
        await context.send(text.PI_CONTROL_UPDATE_BASIC_SUCCESS)
        await send_info_embed(user_auth, planet_int, context)
    elif arg == "full":
        await planet_int.update_pi(context.author.id, user_auth.get_selected(context.author.id), context)
        await send_info_embed(user_auth, planet_int, context)
    else:
        await context.send(f"UPDATE_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg}\". "
                           f"SEND THIS TO ALENTO/SOMBRA GHOSTFLAME!")


async def send_info_embed(user_auth: EVEUserAuthManager, planet_int: PlanetIntManager, context: commands.Context,
                          arg2: str = None):
    if arg2:
        await send_planet_info_embed(user_auth, planet_int, context, arg2)
    else:
        await send_pi_info_embed(user_auth, planet_int, context)


async def send_pi_info_embed(user_auth: EVEUserAuthManager, planet_int: PlanetIntManager, context: commands.Context):
    embed = discord.Embed(title="Planet Info", color=0x8CB1DE)

    pi_info = planet_int.get_pi_info(context.author.id, user_auth.get_selected(context.author.id))
    if not pi_info:
        await context.send(text.PI_CONTROL_LIST_UPDATING)
        await planet_int.update_pi_info(context.author.id, user_auth.get_selected(context.author.id))
        pi_info = planet_int.get_pi_info(context.author.id, user_auth.get_selected(context.author.id))

    for planet_id in pi_info:
        basic_planet = pi_info[planet_id]

        planet_pi = planet_int.get_planet_pi(context.author.id, user_auth.get_selected(context.author.id), planet_id)
        if planet_pi:
            extractor_time = get_lowest_extractor_time(planet_pi)
        else:
            extractor_time = "No data, run `pi update full`"

        name_text = f"{basic_planet.solar_system.name} {basic_planet.planet.index}"
        value_text = f"ID: `{planet_id}`\nType: **{basic_planet.planet_type.capitalize()}**\n" \
                     f"Extractor Status: **{extractor_time}**\nUpgrade Level: {basic_planet.upgrade_level}\n" \
                     f"System Security: {round(basic_planet.solar_system.security, 1)}\n" \
                     f"Building Count: {basic_planet.num_pins}\nLast Updated: {basic_planet.last_update}"
        embed.add_field(name=name_text, value=value_text, inline=True)

    await context.send(embed=embed)


async def send_planet_info_embed(user_auth: EVEUserAuthManager, planet_int: PlanetIntManager, context: commands.Context,
                                 planet_id_string: str):
    planet_id = get_numbers(planet_id_string)
    if not planet_id_string:
        await context.send(text.PI_CONTROL_PLANET_INFO_MISSING_ARG)
    else:
        pi_info = planet_int.get_pi_info(context.author.id, user_auth.get_selected(context.author.id))
        if not pi_info:
            await context.send(text.PI_CONTROL_LIST_UPDATING)
            await planet_int.update_pi_info(context.author.id, user_auth.get_selected(context.author.id))
            pi_info = planet_int.get_pi_info(context.author.id, user_auth.get_selected(context.author.id))

        if planet_id not in pi_info:
            await context.send(text.PI_CONTROL_PLANET_INFO_ID_NOT_IN_PI_INFO)
        else:
            planet_pi = planet_int.get_planet_pi(context.author.id, user_auth.get_selected(context.author.id),
                                                 planet_id)
            if not planet_pi:
                await context.send(text.PI_CONTROL_PLANET_INFO_UPDATING)
                await planet_int.update_pi_planet(context.author.id, user_auth.get_selected(context.author.id),
                                                  planet_id)
                planet_pi = planet_int.get_planet_pi(context.author.id, user_auth.get_selected(context.author.id),
                                                     planet_id)
            basic_planet = pi_info[planet_id]
            embed_title = f"{basic_planet.solar_system.name} {basic_planet.planet.index} " \
                          f"({basic_planet.planet_type.capitalize()})"
            embed = discord.Embed(title=embed_title, color=0x8CB1DE)
            extractor_text = ""
            factory_text = ""
            other_text = ""
            for pin in planet_pi.pins:

                if isinstance(pin, FactoryInfo):
                    if not pin.type:
                        logger.debug(f"DEBUG {pin.__dict__}")
                    # factory_text += f"{pin.type.name}\n"
                    factory_text += get_factory_text(pin)
                elif isinstance(pin, ExtractorInfo):
                    extractor_text += get_extractor_text(pin)
                elif isinstance(pin, BasicPinInfo):
                    other_text += f"{pin.type.name}\n"
                else:
                    raise NotADirectoryError(f"The following type is unimplemented: {type(pin)}")

            if extractor_text:
                embed.add_field(name="Extractors", value=f"```{extractor_text}```", inline=False)
            else:
                embed.add_field(name="Extractors", value="None", inline=False)

            if factory_text:
                embed.add_field(name="Factories", value=f"```{factory_text}```", inline=False)
            else:
                embed.add_field(name="Factories", value="None", inline=False)

            if other_text:
                embed.add_field(name="Other", value=f"```{other_text}```", inline=False)
            else:
                embed.add_field(name="Other", value="None", inline=False)

            await context.send(embed=embed)


def get_time_remaining_text(time: timedelta) -> str:
    output_str = ""

    if time.days:
        output_str += f"{time.days} days, "
    if time.seconds // 3600:
        output_str += f"{time.seconds // 3600} hours, "
    output_str += f"{time.seconds % 3600 // 60} minutes."

    return output_str


def get_extractor_text(extractor: ExtractorInfo) -> str:
    output_string = ""

    output_string += f"{extractor.type.name}\n"
    if datetime.utcnow() < extractor.expiry_time:
        time_remaining = extractor.expiry_time - datetime.utcnow()
        output_string += f"  Status: Running\n" \
                         f"  Time Remaining: {get_time_remaining_text(time_remaining)}\n"
    else:
        output_string += f"  Status: Idle\n  Time Remaining: None\n"

    if extractor.product_type:
        output_string += f"  Product: {extractor.product_type.name}\n"
    elif extractor.product_type_id:
        output_string += f"  Product: {extractor.product_type_id} (Name not found?)\n"
    else:
        output_string += f"  Product: None\n"

    output_string += f"  Quantity per Cycle: {extractor.quantity_per_cycle}\n"

    output_string += f"  Head Count: {extractor.head_count}\n"

    return output_string


def get_factory_text(factory: FactoryInfo) -> str:
    output_string = ""

    output_string += f"{factory.type.name}\n"
    if factory.schematic:
        output_string += f"  Schematic: {factory.schematic.name}\n"
    elif factory.schematic_id:
        output_string += f"  Schematic: {factory.schematic_id}\n"
    else:
        output_string += f"  Schematic: None\n"

    return output_string


def get_lowest_extractor_time(planet_pi: PlanetPIInfo):
    lowest_time_left = datetime.utcnow()
    found_extractor = False
    changed_lowest_time = False

    for pin in planet_pi.pins:
        if isinstance(pin, ExtractorInfo):
            found_extractor = True
            if pin.expiry_time > lowest_time_left:
                lowest_time_left = pin.expiry_time
                changed_lowest_time = True

    if changed_lowest_time:
        return get_time_remaining_text(lowest_time_left - datetime.utcnow())
    elif found_extractor:
        return "Idle"
    else:
        return "No Extractors."


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
