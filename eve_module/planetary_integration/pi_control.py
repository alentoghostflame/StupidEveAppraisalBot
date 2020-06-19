from eve_module.storage import EVEUserAuthManager, ESIUnauthorized
from eve_module.planetary_integration import text
from discord.ext import commands
import logging
import aiohttp
import discord


logger = logging.getLogger("main_bot")


async def pi_control(user_auth: EVEUserAuthManager, session: aiohttp.ClientSession, context: commands.Context,
                     arg1: str, arg2: str):
    user_scopes = user_auth.get_selected_scopes(context.author.id)
    if not user_scopes:
        await context.send(text.NO_AUTH_SELECTED_CHARACTER)
    elif arg1 not in {"enable", "disable", "list", "planet"}:
        await context.send(text.PI_CONTROL_MISSING_ARG_1)
    elif user_scopes.get("esi-planets.manage_planets.v1", None) is None:
        await context.send(text.AUTH_SCOPE_MISSING.format("esi-planets.manage_planets.v1"))
    elif arg1 == "enable":
        await enable_pi(user_auth, context)
    elif not user_scopes.get("esi-planets.manage_planets.v1", None):
        await context.send(text.PI_CONTROL_SCOPE_FALSE)
    elif arg1 == "disable":
        await disable_pi(user_auth, context)
    elif arg1 == "list":
        await send_list_embed(user_auth, session, context)
    elif arg1 == "planet":
        pass
    else:
        await context.send(f"PI_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\". SEND THIS TO ALENTO/SOMBRA GHOSTFLAME!")
    """
    pi:
        enable
        disable
        list
        planet id/name
    """


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


async def send_list_embed(user_auth: EVEUserAuthManager, session: aiohttp.ClientSession, context: commands.Context):
    embed = discord.Embed(title="Planet Info", color=0x8CB1DE)

    base_url = "https://esi.evetech.net/latest/characters/{}/planets/"
    character_id = user_auth.get_selected(context.author.id)
    token = await user_auth.get_access_token(context.author.id, character_id)
    response = await session.get(url=base_url.format(character_id), params={"token": token})
    raw_data = await response.json()
    response.close()
    print(raw_data)

    # await context.send(embed=embed)

