import os
import openai
from config import OPENAI_API_KEY, WHISPER_MODEL, TEMP_DIR

openai.api_key = OPENAI_API_KEY


def create_subtitles(audio_path, translations):
    subtitle_files = {}

    # Create original language subtitles
    original_srt = create_srt_file(audio_path)
    subtitle_files["Original"] = original_srt

    # Create translated subtitles
    for lang, translation in translations.items():
        translated_srt = translate_srt(original_srt, lang)
        subtitle_files[lang] = translated_srt

    return subtitle_files


def create_srt_file(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            WHISPER_MODEL,
            audio_file,
            response_format="srt"
        )

    file_path = os.path.join(TEMP_DIR, "original_subtitles.srt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(transcript)

    return transcript


def translate_srt(srt_content, target_language):
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system",
             "content": f"You are a professional translator. Translate the following SRT content to {target_language}. Maintain the SRT format, including timecodes."},
            {"role": "user", "content": srt_content}
        ]
    )
    translated_srt = response.choices[0].message.content

    file_path = os.path.join(TEMP_DIR, f"{target_language.lower()}_subtitles.srt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(translated_srt)

    return translated_srt