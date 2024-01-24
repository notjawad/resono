import whisper
import discord

from whisper.utils import get_writer

model = whisper.load_model("base")


async def get_transcripts_from_audio_data(
    file_paths: list, cxt: discord.ApplicationContext
) -> list:
    all_transcripts = []

    for file_path in file_paths:
        result = model.transcribe(file_path)
        user = await cxt.guild.fetch_member(int(file_path.split("/")[-1].split(".")[0]))

        all_transcripts.append(
            {
                "transcript": result["text"],
                "user_id": user.id,
                "user_name": user.name,
            }
        )

    return all_transcripts
