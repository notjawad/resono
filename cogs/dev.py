import discord

from discord.ext import commands
from discord import slash_command
from utils import emojis


class LogsPaginator(discord.ui.View):
    def __init__(self, pages: list[str]):
        super().__init__()
        self.pages = pages
        self.current_page = 0

    @discord.ui.button(emoji=emojis.prev, style=discord.ButtonStyle.gray)
    async def previous(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.current_page == 0:
            return

        self.current_page -= 1
        await self.update_page(interaction)

    @discord.ui.button(emoji=emojis.next, style=discord.ButtonStyle.gray)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page == len(self.pages) - 1:
            return

        self.current_page += 1
        await self.update_page(interaction)

    @discord.ui.button(label="Clear Logs", style=discord.ButtonStyle.red)
    async def clear(self, button: discord.ui.Button, interaction: discord.Interaction):
        with open("bot.log", "w", encoding="utf-8") as f:
            f.write("")

        await interaction.response.edit_message(content="Cleared logs.", view=None)

    async def update_page(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=f"```py\n{self.pages[self.current_page]}```"
        )


class Dev(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @slash_command(name="logs", description="Get the logs of the bot", hidden=True)
    @commands.is_owner()
    async def _logs(self, ctx: discord.ApplicationContext):
        with open("bot.log", "r", encoding="utf-8") as f:
            logs = f.read()

        if not logs:
            return await ctx.respond("Logs are empty.", ephemeral=True)

        logs = logs.split("\n")
        logs.reverse()

        pages = []
        for i in range(0, len(logs), 10):
            pages.append("\n".join(logs[i : i + 10]))

        view = LogsPaginator(pages)
        await ctx.send(content=f"```py\n{pages[0]}```", view=view)

    @slash_command(name="reload", description="Reloads a cog", hidden=True)
    @commands.is_owner()
    async def _reload(
        self,
        ctx: discord.ApplicationContext,
        cog: discord.Option(str, description="The cog to reload"),
    ):
        try:
            self.bot.reload_extension(f"cogs.{cog}")
        except Exception as e:
            return await ctx.respond(f"Failed to reload cog: {e}", ephemeral=True)

        await ctx.respond(f"Reloaded cog: {cog}")


def setup(bot: discord.Bot):
    bot.add_cog(Dev(bot))
