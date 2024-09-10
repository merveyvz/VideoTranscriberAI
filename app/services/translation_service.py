import re

from openai import OpenAI
from app.config import OPENAI_API_KEY, GPT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


class TranslationService:
    @staticmethod
    def translate_text(text, target_language):
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system",
                 "content": f"You are a translator. Translate the following text to {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content

    @staticmethod
    def translate_srt(srt_content, target_language):
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system",
                 "content": f"You are a translator. Translate the following SRT subtitle content to {target_language}. Maintain the SRT format and timing."},
                {"role": "user", "content": srt_content}
            ]
        )
        return response.choices[0].message.content

    @staticmethod
    def format_srt(translations):
        formatted_srt = ""
        for i, (timestamp, text) in enumerate(translations, start=1):
            formatted_srt += f"{i}\n{timestamp}\n{text}\n\n"
        return formatted_srt.strip()

    @staticmethod
    def translate_content(transcript, srt_content, target_languages):
        translations = {}
        for lang in target_languages:
            translated_text = TranslationService.translate_text(transcript, lang)

            # Parse the original SRT content
            srt_parts = re.findall(
                r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?:\n\n|\Z)', srt_content)

            # Translate each subtitle text
            translated_parts = []
            for _, timestamp, text in srt_parts:
                translated_subtitle = TranslationService.translate_text(text, lang)
                translated_parts.append((timestamp, translated_subtitle))

            # Format the translated parts into a valid SRT
            translated_srt = TranslationService.format_srt(translated_parts)

            translations[lang] = {"text": translated_text, "srt": translated_srt}
        return translations