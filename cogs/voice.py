import discord
import time
import random
import os


from discord.ext import commands
from discord import slash_command
from utils.embeds import Embeds as e
from utils.utils import get_transcripts_from_audio_data
from gpt4all import GPT4All


model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")


class RecorderControls(discord.ui.View):
    def __init__(self, bot: discord.Bot, ctx: discord.ApplicationContext):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.db = bot.db
        self.stopped = True

    async def finished_callback(self, sink: discord.sinks.WaveSink, interaction):
        await self.ctx.respond("Finished recording!")
        await self.ctx.voice_client.disconnect()

        file_paths = []

        for user_id in list(sink.audio_data.keys()):
            dir_path = f"recordings/{self.ctx.guild.id}"
            os.makedirs(dir_path, exist_ok=True)

            file_path = f"{dir_path}/{user_id}.mp3"
            with open(file_path, "wb") as audio_file:
                audio_file.write(sink.audio_data[user_id].file.read())

            file_paths.append(file_path)
            transcripts = await get_transcripts_from_audio_data(file_paths, self.ctx)

            transcripts = "\n".join(
                [
                    f"{transcript['user_name']}: {transcript['transcript']}"
                    for transcript in transcripts
                ]
            )

            prompt = f"Provide me point wise summary of meeting with proper title from this text: \n{transcripts}"

            output = model.generate(prompt)

            print(output)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start_stop(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.stopped:
            await self.start_recording(button, interaction)
        else:
            await self.stop_recording(button, interaction)

    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.green)
    async def transcript(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await self.ctx.respond("Transcript")

    async def start_recording(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.stopped = False
        button.label, button.style = "Stop", discord.ButtonStyle.red
        button.disabled = False

        self.ctx.voice_client.start_recording(
            discord.sinks.WaveSink(),
            lambda sink: self.finished_callback(sink, interaction),
        )

        await interaction.response.edit_message(content="Recording started!", view=self)

    async def stop_recording(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.stopped = True
        button.label, button.style = "Start", discord.ButtonStyle.green
        button.disabled = False

        self.ctx.voice_client.stop_recording()

        await interaction.response.edit_message(content="Recording stopped!", view=self)


class Voice(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db = bot.db
        self.log = bot.log

    def generate_error_id(self):
        timestamp = int(time.time())
        random_number = random.randint(1, 1000000)
        return f"{timestamp}-{random_number}"

    @slash_command(name="setup", description="Starts the setup process for your server")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setup(
        self,
        ctx: discord.ApplicationContext,
        summary_channel: discord.Option(
            discord.TextChannel,
            description="The channel to send the summary in",
            required=True,
        ),
        send_to_all: discord.Option(
            bool,
            description="Whether to send the summary to all participants or just the channel",
            required=True,
        ),
    ):
        await ctx.defer()

        try:
            await self.db.guilds.update(
                {"guild_id": ctx.guild.id},
                {
                    "$set": {
                        "summary_channel": summary_channel.id,
                        "send_to_all": send_to_all,
                    }
                },
            )

            self.log.info(f"Updated {ctx.guild.name} ({ctx.guild.id}) in the database")

            await ctx.respond("Setup complete! Use `/help` to get started.")
        except Exception as error:
            error_id = self.generate_error_id()
            self.log.error(f"{error}: {error_id}")
            await ctx.respond(
                embed=e.error(
                    "An error occurred while setting up your server.",
                    error_id=error_id,
                ),
                ephemeral=True,
            )
            return

    @slash_command(name="join", description="Joins the voice channel you are in")
    @commands.guild_only()
    async def join(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        if ctx.author.voice is None:
            return await ctx.respond(
                "You must be in a voice channel to use this command.", ephemeral=True
            )

        try:
            await ctx.author.voice.channel.connect()

            view = RecorderControls(self.bot, ctx)

            await ctx.respond("Connected!", view=view)

        except Exception as error:
            error_id = self.generate_error_id()
            self.log.error(f"{error}: {error_id}")
            await ctx.respond(
                embed=e.error(
                    "An error occurred while joining the voice channel.",
                    error_id=error_id,
                ),
                ephemeral=True,
            )
            return


def setup(bot: discord.Bot):
    bot.add_cog(Voice(bot))
