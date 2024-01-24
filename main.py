import discord
import os
import motor.motor_asyncio

from discord.ext import commands
from dotenv import load_dotenv
from utils.logger_config import configure_logger

load_dotenv()


class Resono(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix="r!",
            intents=discord.Intents.all(),
            case_insensitive=True,
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="/help 💬"
            ),
        )

        self.log = configure_logger()

        self.db = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("mongo_uri"))[
            "resono"
        ]

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                # try:
                self.load_extension(f"cogs.{filename[:-3]}")
                self.log.info(f"Loaded {filename}")
            # except Exception as e:

            #     self.log.error(f"Failed to load {filename}: {e}")

    async def on_ready(self):
        self.log.info(f"Logged in as {self.user} ({self.user.id})")
        self.log.info(f"Connected to {len(self.guilds)} guilds")


bot = Resono()
bot.run(os.getenv("bot_token"))
