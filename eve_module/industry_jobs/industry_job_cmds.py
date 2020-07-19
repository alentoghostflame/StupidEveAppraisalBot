from evelib import EVEManager
from eve_module.storage import EVEUserAuthManager
from eve_module.industry_jobs import text
from discord.ext import commands
from datetime import datetime, timedelta
import logging
import discord


logger = logging.getLogger("main_bot")


async def send_help_embed(context: commands.Context):
    embed = discord.Embed(title="Industry Jobs", color=0x43464B)

    embed.add_field(name="Description", value=text.INDUSTRY_JOBS_HELP_DESCRIPTION, inline=False)
    embed.add_field(name="Permissions", value=text.INDUSTRY_JOBS_HELP_PERMISSIONS, inline=False)
    embed.add_field(name="Information", value=text.INDUSTRY_JOBS_HELP_INFORMATION, inline=False)

    await context.send(embed=embed)


async def enable_industry(user_auth: EVEUserAuthManager, context: commands.Context):
    if user_auth.set_selected_desired_scope(context.author.id, "esi-industry.read_character_jobs.v1", True):
        await context.send(text.INDUSTRY_JOBS_ENABLED)
    else:
        await context.send(text.INDUSTRY_JOBS_TOGGLE_FAIL)


async def disable_industry(user_auth: EVEUserAuthManager, context: commands.Context):
    if user_auth.set_selected_desired_scope(context.author.id, "esi-industry.read_character_jobs.v1", False):
        await context.send(text.INDUSTRY_JOBS_DISABLED)
    else:
        await context.send(text.INDUSTRY_JOBS_TOGGLE_FAIL)


async def send_industry_info_embed(eve_manager: EVEManager, user_auth: EVEUserAuthManager, context: commands.Context):
    token = await user_auth.get_access_token(context.author.id, user_auth.get_selected(context.author.id))
    industry_jobs = await eve_manager.esi.industry.get_character_jobs(user_auth.get_selected(context.author.id), token)
    if industry_jobs:
        output_string = ""
        for job in industry_jobs:
            output_string += f"{job.product_type.name}\n  Activity: {job.activity_string}\n" \
                             f"  Status: {job.status.capitalize()}\n"
            if job.status == "active" and job.end_date > datetime.utcnow():
                output_string += f"  Time Remaining: {get_time_remaining_text(job.end_date - datetime.utcnow())}\n"
            else:
                output_string += f"  Time Remaining: None\n"
        if output_string:
            await context.send(f"```{output_string}```")
        else:
            await context.send(text.INDUSTRY_JOBS_INFO_EMPTY)
    else:
        await context.send(text.INDUSTRY_JOBS_INFO_EMPTY)


def get_time_remaining_text(time: timedelta) -> str:
    output_str = ""

    if time.days:
        if time.days > 1:
            output_str += f"{time.days} days, "
        else:
            output_str += f"{time.days} day, "
    if time.seconds // 3600:
        if time.seconds // 3600 > 1:
            output_str += f"{time.seconds // 3600} hours, "
        else:
            output_str += f"{time.seconds // 3600} hour, "
    if time.seconds % 3600 // 60 > 1:
        output_str += f"{time.seconds % 3600 // 60} minutes."
    else:
        output_str += f"{time.seconds % 3600 // 60} minute."

    return output_str
