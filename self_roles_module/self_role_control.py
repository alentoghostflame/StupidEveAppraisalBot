from self_roles_module.storage import RoleSelfAssignData
from self_roles_module import text
from discord.ext import commands
import logging
import discord
import typing
import re


logger = logging.getLogger("main_bot")


async def self_role_control(guild_data: RoleSelfAssignData, context: commands.Context, arg1: str, arg2: str, arg3: str):
    if not arg1 or (arg1 not in {"list", "add", "remove"} and arg1.lower() not in guild_data.roles):
        await context.send(text.SELF_ROLE_CONTROL_MISSING_ARG_1)
    elif arg1 == "list":
        await send_list_embed(guild_data, context)
    elif arg1.lower() in guild_data.roles:
        await toggle_user_role(guild_data, context, arg1)
    elif not context.author.guild_permissions.administrator:
        # raise commands.MissingPermissions(discord.)
        await context.send(text.MISSING_ADMIN_PERMISSION)
    elif arg1 == "add":
        await add_self_role(guild_data, context, arg2, arg3)
    elif arg1 in {"remove", "rm"}:
        await remove_self_role(guild_data, context, arg2)
    else:
        await context.send(f"SELF_ROLE_CONTROL: ALL ELIFS PASSED, YOU HAVE A HOLE SOMEWHERE! \"{arg1}\", "
                           f"\"{arg2}\", \"{arg3}\". SEND THIS TO ALENTO/SOMBRA GHOSTFLAME!")

    """
    role:
        role_name, toggles the role being on the user.
        list, list roles
        ADMIN PERMISSION GATE
        add, adds a keyword/role
        remove | rm, removes a keyword/role
    """


async def send_list_embed(guild_data: RoleSelfAssignData, context: commands.Context):
    embed = discord.Embed(title="Role List")
    guild: discord.Guild = context.guild

    if guild_data.roles:
        temp_string = ""
        for role_keyword in guild_data.roles:
            role = guild.get_role(guild_data.roles[role_keyword])
            if role:
                temp_string += f"{role_keyword} | {role.mention}\n"
            else:
                temp_string += f"{role_keyword} | {guild_data.roles[role_keyword]}\n"
        embed.add_field(name="Keyword | Role", value=temp_string)
    else:
        embed.add_field(name="Keyword | Role", value="None | None")

    await context.send(embed=embed)


async def toggle_user_role(guild_data: RoleSelfAssignData, context: commands.Context, role_keyword: str):
    role_id = guild_data.roles[role_keyword.lower()]
    role = context.guild.get_role(role_id)
    if role:
        if role in context.author.roles:
            await context.author.remove_roles(role, reason="They asked for it, really!")
            await context.send(text.SELF_ROLE_CONTROL_TOGGLE_REMOVED)
        else:
            await context.author.add_roles(role, reason="They asked for it.")
            await context.send(text.SELF_ROLE_CONTROL_TOGGLE_ADDED)
    else:
        await context.send(text.SELF_ROLE_CONTROL_TOGGLE_ROLE_DOESNT_EXIST)


async def add_self_role(guild_data: RoleSelfAssignData, context: commands.Context, role_keyword: str,
                        role_mention: str):
    role_id = get_numbers(role_mention)
    if not role_keyword or not role_id:
        print(f"{role_keyword}, {role_mention}, {role_id}")
        await context.send(text.SELF_ROLE_CONTROL_ADD_MISSING_ARGS)
    else:
        role = context.guild.get_role(role_id)
        if role:
            guild_data.roles[role_keyword.lower()] = role_id
            await context.send(text.SELF_ROLE_CONTROL_ADD_SUCCESS.format(role_keyword.lower()))
        else:
            await context.send(text.ROLE_DOESNT_EXIST)


async def remove_self_role(guild_data: RoleSelfAssignData, context: commands, role_keyword: str):
    if not role_keyword:
        await context.send(text.SELF_ROLE_CONTROL_REMOVE_MISSING_ARG)
    elif role_keyword not in guild_data.roles:
        await context.send(text.SELF_ROLE_CONTROL_REMOVE_NOT_FOUND.format(role_keyword.lower()))
    else:
        guild_data.roles.pop(role_keyword.lower())
        await context.send(text.SELF_ROLE_CONTROL_REMOVE_SUCCESS.format(role_keyword.lower()))


def get_numbers(string: str) -> typing.Optional[int]:
    if string:
        comp = re.compile("(\\d+)")
        num_list = comp.findall(string)

        if num_list:
            return int("".join(num_list))
    return None
