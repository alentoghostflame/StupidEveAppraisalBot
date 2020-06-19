from alento_bot import DiscordBot
from alento_bot import CoreCog
from self_roles_module import SelfRoleModule
from eve_module import EVEModule
import logging


logger = logging.getLogger("main_bot")
discord_bot = DiscordBot()
self_roles = SelfRoleModule(discord_bot)
eve = EVEModule(discord_bot)


try:

    discord_bot.add_cog(CoreCog(discord_bot.storage))

    self_roles.register_cogs()
    eve.register_cogs(discord_bot)

    discord_bot.load()
    eve.load()

    discord_bot.run()
except Exception as e:
    logger.critical("SOMETHING TERRIBLE HAPPENED!")
    logger.exception(e)
    raise e
finally:
    eve.save()
    discord_bot.save()
