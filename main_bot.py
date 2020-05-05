from discord.ext import commands
import user_commands
import storage
import logging


logger = logging.getLogger("Main")


class StupidEveAppraisalBot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=";", case_insensitive=True)
        self.storage = storage.StorageManager()

        self.bot.add_cog(user_commands.MiscCog(self.bot))
        self.bot.add_cog(user_commands.MarketCog(self.bot, self.storage.sde))

    def load(self):
        self.storage.load()

    def save(self):
        pass

    def run(self):
        passed_checks: bool = True
        if not self.storage.disk.config.token:
            logger.critical("Token missing from config, can't start bot.")
            passed_checks = False
        if not self.storage.sde.loaded:
            logger.critical("EVE's Static Data Export (sde) not found, can't start bot.")
            passed_checks = False

        if passed_checks:
            logger.info("Starting bot loop.")
            self.bot.run(self.storage.disk.config.token)
