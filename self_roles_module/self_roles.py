from self_roles_module.self_role_control import self_role_control
from self_roles_module import text
from self_roles_module.storage import RoleSelfAssignData
from alento_bot import DiscordBot, StorageManager
from discord.ext import commands
import logging


logger = logging.getLogger("main_bot")


class SelfRoleModule:
    def __init__(self, discord_bot: DiscordBot):
        self.discord_bot: DiscordBot = discord_bot

        self.discord_bot.storage.guilds.register_data_name("self_roles_data", RoleSelfAssignData)

    def register_cogs(self):
        logger.info("Registering SelfRole cog.")
        self.discord_bot.add_cog(SelfRoleCog(self.discord_bot.storage))


class SelfRoleCog(commands.Cog, name="Self Roles"):
    def __init__(self, storage: StorageManager):
        self.storage: StorageManager = storage

    @commands.command(name="self_role", aliases=["role", ])
    async def self_role_command(self, context: commands.Context, arg1=None, arg2=None, arg3=None):
        guild_data: RoleSelfAssignData = self.storage.guilds.get(context.guild.id, "self_roles_data")
        await self_role_control(guild_data, context, arg1, arg2, arg3)

    @self_role_command.error
    async def self_role_err(self, context: commands.Context, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await context.send(text.MISSING_ADMIN_PERMISSION)
        else:
            await context.send(f"ERROR OCCURED: {type(error)}, {error}\nREPORT THIS TO SOMBRA/ALENTO GHOSTFLAME!")
            raise error
