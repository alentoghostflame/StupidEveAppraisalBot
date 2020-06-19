from alento_bot import DiscordBot
from eve_module.storage import EVEAuthManager, EVEConfig, UniverseStorage, ItemStorage, MarketManager, \
    EVEUserAuthManager
from eve_module.planetary_integration import EVEPlanetaryIntegrationCog
from eve_module.user_auth import EVEAuthCog
from eve_module.market import EVEMarketCog
from eve_module.misc import EVEMiscCog
import logging
import aiohttp
import asyncio


logger = logging.getLogger("main_bot")


class EVEModule:
    def __init__(self, discord_bot: DiscordBot):
        self.discord_bot: DiscordBot = discord_bot

        self.session = aiohttp.ClientSession()

        # noinspection PyArgumentList
        self.eve_config: EVEConfig = EVEConfig(self.discord_bot.storage.config)
        self.discord_bot.storage.caches.register_cache(self.eve_config, "eve_config")
        self.universe: UniverseStorage = UniverseStorage(self.discord_bot.storage, self.eve_config)
        self.auth: EVEAuthManager = EVEAuthManager(self.discord_bot.storage)
        self.user_auth: EVEUserAuthManager = EVEUserAuthManager(self.discord_bot.storage, self.session)
        self.items: ItemStorage = ItemStorage(self.discord_bot.storage)
        self.market = MarketManager(self.eve_config, self.auth)

    def register_cogs(self, discord_bot: DiscordBot):
        logger.info("Registering cogs for EVE")
        discord_bot.add_cog(EVEMiscCog())
        discord_bot.add_cog(EVEMarketCog(self.discord_bot.storage, self.universe, self.items, self.market))
        discord_bot.add_cog(EVEAuthCog(self.discord_bot.storage, self.auth, self.user_auth))
        discord_bot.add_cog(EVEPlanetaryIntegrationCog(self.discord_bot.storage, self.user_auth))

    def load(self):
        self.auth.load()
        self.universe.load()
        self.items.load()

    def save(self):
        # self.user_auth.save()
        # loop = asyncio.new_event_loop()
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.session.close())
