from openai import OpenAI
from app.config import OPENAI_API_KEY, GPT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def translate_text(text, target_language):
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system",
             "content": f"You are a professional translator. Translate the following text to {target_language}."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content


def translate_srt(srt_content, target_language):
    if not srt_content:
        return None
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system",
             "content": f"You are a professional translator. Translate the following SRT content to {target_language}. Maintain the SRT format, including timecodes."},
            {"role": "user", "content": srt_content}
        ]
    )
    return response.choices[0].message.content
