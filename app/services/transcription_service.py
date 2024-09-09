from openai import OpenAI
from app.config import OPENAI_API_KEY, WHISPER_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_file,
            response_format="text"
        )
    return transcript


def create_srt(audio_path):
    with open(audio_path, "rb") as audio_file:
        srt_content = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_file,
            response_format="srt"
        )

    # Validate SRT content
    if not srt_content or not srt_content.strip():
        raise ValueError("Generated SRT content is empty")

    # Check if the SRT content has the correct format
    lines = srt_content.strip().split('\n')
    if len(lines) < 4 or not lines[0].isdigit() or '-->' not in lines[1]:
        raise ValueError("Generated SRT content is not in the correct format")

    return srt_content

