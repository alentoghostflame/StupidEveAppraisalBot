from alento_bot import DiscordBot
from alento_bot import CoreCog
from eve_module import EVEModule
import logging


logger = logging.getLogger("main_bot")
discord_bot = DiscordBot()


try:

    discord_bot.add_cog(CoreCog(discord_bot.storage))

    eve = EVEModule(discord_bot.storage)
    eve.register_cogs(discord_bot)

    discord_bot.load()
    eve.load()

    discord_bot.run()
except Exception as e:
    logger.critical("SOMETHING TERRIBLE HAPPENED!")
    logger.exception(e)
    raise e
finally:
    discord_bot.save()
