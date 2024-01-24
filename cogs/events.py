import discord

from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db = bot.db
        self.log = bot.log

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.db.guilds.insert_one(
            {
                "guild_id": guild.id,
                "premium": False,
                "summary_channel": None,
                "send_to_all": False,
                "previous_summaries": [],
                "mod_roles": [],
            }
        )

        self.log.info(f"Added {guild.name} ({guild.id}) to the database")


def setup(bot: discord.Bot):
    bot.add_cog(Events(bot))
