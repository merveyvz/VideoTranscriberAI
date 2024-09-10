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
                 "content": f"You are a translator. Translate the following text to {target_language}. "
                            f"Provide only the translation without any introductory text. Do not add any other"
                            f" information. I want only the translated text."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def translate_srt(srt_content, target_language):
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system",
                 "content": f"You are a translator. Translate the following SRT subtitle content to {target_language}. "
                            f"Maintain the SRT format and timing. Provide only the translated SRT content without any "
                            f"introductory text. Do not add any other information. I want only the translated SRT "
                            f"content."},
                {"role": "user", "content": srt_content}
            ]
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def translate_content(transcript, srt_content, target_languages):
        translations = {}

        for lang in target_languages:
            # Translate transcript
            translated_text = TranslationService.translate_text(transcript, lang)

            # Translate SRT content
            translated_srt = TranslationService.translate_srt(srt_content, lang)

            translations[lang] = {"text": translated_text, "srt": translated_srt}

        return translations
