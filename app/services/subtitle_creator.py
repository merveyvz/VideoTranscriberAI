
import pysrt
from datetime import timedelta
import re


def timedelta_to_srt_time(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def create_srt(transcript, lang):
    subs = pysrt.SubRipFile()

    # Split transcript into sentences
    sentences = re.split('(?<=[.!?]) +', transcript)

    current_time = timedelta(seconds=0)
    for i, sentence in enumerate(sentences, start=1):
        # Estimate duration based on sentence length (assuming average speaking speed)
        word_count = len(sentence.split())
        duration = timedelta(seconds=max(1, min(10, word_count * 0.5)))  # Between 1 and 10 seconds

        end_time = current_time + duration

        # Create subtitle item
        sub = pysrt.SubRipItem(
            index=i,
            start=timedelta_to_srt_time(current_time),
            end=timedelta_to_srt_time(end_time),
            text=sentence
        )

        # Apply language-specific formatting
        if lang in ['zh', 'ja', 'ko']:  # Chinese, Japanese, Korean
            sub.text = sub.text.replace(' ', '')  # Remove spaces for these languages
        elif lang in ['ar', 'he']:  # Arabic, Hebrew
            sub.text = sub.text[::-1]  # Reverse text for right-to-left languages

        subs.append(sub)

        current_time = end_time

    return subs