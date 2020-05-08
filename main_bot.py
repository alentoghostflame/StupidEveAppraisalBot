from discord.ext import commands
import user_commands
# import utilities
import logging
import storage_module


logger = logging.getLogger("Main")


class StupidEveAppraisalBot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=";", case_insensitive=True)
        self.storage = storage_module.StorageManager()

        self.bot.add_cog(user_commands.MiscCog(self.bot))
        # self.bot.add_cog(user_commands.MarketCog(self.bot, self.storage.sde, self.storage.disk.eve_auth))
        self.bot.add_cog(user_commands.MarketCog(self.storage))
        self.bot.add_cog(storage_module.TasksCog(self.storage))

    def load(self):
        self.storage.load()

    def save(self):
        self.storage.save()

    def run(self):
        passed_checks: bool = True
        if not self.storage.config.discord_token:
            logger.critical("Token missing from config, can't start bot.")
            passed_checks = False
        if not self.storage.sde.loaded:
            logger.critical("EVE's Static Data Export (sde) not found, can't start bot.")
            passed_checks = False

        if passed_checks:
            logger.info("Starting bot loop.")
            self.bot.run(self.storage.config.discord_token)
