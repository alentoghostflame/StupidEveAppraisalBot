from discord.ext import commands
import logging


logger = logging.getLogger("Main")


class MiscCog(commands.Cog, name="Misc"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping", brief="Quick command to test the bot.")
    async def ping(self, context):
        await context.send("Pong!")

    @commands.command(name="github", brief="Quick command to link the github URL.")
    async def github(self, context):
        await context.send("<https://github.com/alentoghostflame/StupidEveAppraisalBot>")
