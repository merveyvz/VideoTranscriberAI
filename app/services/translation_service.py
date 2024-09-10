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
        return response.choices[0].message.content

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

        # Batch translate transcript for all languages
        transcript_translations = TranslationService.batch_translate_text(transcript, target_languages)

        # Parse the original SRT content
        srt_parts = re.findall(
            r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?:\n\n|\Z)', srt_content)

        # Batch translate all subtitle texts for all languages
        subtitle_texts = [text for _, _, text in srt_parts]
        subtitle_translations = TranslationService.batch_translate_text_multi(subtitle_texts, target_languages)

        for lang in target_languages:
            translated_text = transcript_translations[lang]

            # Create translated parts for SRT
            translated_parts = []
            for i, (_, timestamp, _) in enumerate(srt_parts):
                translated_subtitle = subtitle_translations[lang][i]
                translated_parts.append((timestamp, translated_subtitle))

            # Format the translated parts into a valid SRT
            translated_srt = TranslationService.format_srt(translated_parts)

            translations[lang] = {"text": translated_text, "srt": translated_srt}

        return translations

    @staticmethod
    def batch_translate_text(text, target_languages):
        messages = [
            {"role": "system", "content": f"You are a professional translator. Translate the following text to target "
                                          f"language."}]

        for lang in target_languages:
            messages.append({"role": "user", "content": f"Translate to {lang}: {text}"})

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages
        )

        translations = {}
        for i, lang in enumerate(target_languages):
            translations[lang] = response.choices[i].message.content

        return translations

    @staticmethod
    def batch_translate_text_multi(texts, target_languages):
        messages = [{"role": "system",
                     "content": f"You are a professional translator. Translate the following SRT content to "
                                f"to target language. Maintain the SRT format, including timecodes."}]
        for lang in target_languages:
            lang_texts = [f"{i + 1}. {text}" for i, text in enumerate(texts)]
            messages.append({"role": "user", "content": f"Translate to {lang}:\n" + "\n".join(lang_texts)})

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages
        )

        translations = {lang: [] for lang in target_languages}
        for i, lang in enumerate(target_languages):
            translated_texts = response.choices[i].message.content.split("\n")
            translations[lang] = [text.split(". ", 1)[1] if ". " in text else text for text in translated_texts]

        return translations