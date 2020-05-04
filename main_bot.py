from discord.ext import commands
import storage
import logging


logger = logging.getLogger("Main")


class StupidEveAppraisalBot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=";", case_insensitive=True)
        self.storage = storage.StorageManager()

    def load(self):
        self.storage.load()

    def save(self):
        pass

    def run(self):
        if not self.storage.disk.config.token:
            logger.critical("Token missing from config, can't start bot.")
        else:
            logger.info("Starting bot loop.")
            self.bot.run(self.storage.disk.config.token)
