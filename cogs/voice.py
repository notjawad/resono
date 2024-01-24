import discord

from discord.ext import commands
from discord import slash_command


class Voice(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db = bot.db


def setup(bot: discord.Bot):
    bot.add_cog(Voice(bot))
