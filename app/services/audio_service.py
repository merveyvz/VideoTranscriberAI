import os
from pydub import AudioSegment
from openai import OpenAI
from app.config import OPENAI_API_KEY, WHISPER_MODEL, TEMP_DIR

client = OpenAI(api_key=OPENAI_API_KEY)


class AudioService:
    @staticmethod
    def split_audio(file_path, chunk_length_ms=60000):  # 60 seconds
        audio = AudioSegment.from_wav(file_path)
        chunks = []
        for i, chunk in enumerate(audio[::chunk_length_ms]):
            chunk_path = os.path.join(TEMP_DIR, f"chunk_{i}.wav")
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
        return chunks

    @staticmethod
    def transcribe_audio(audio_path):
        chunks = AudioService.split_audio(audio_path)
        full_transcript = ""
        for chunk in chunks:
            with open(chunk, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio_file
                )
            full_transcript += transcript.text + " "
            os.remove(chunk)  # Clean up the chunk file
        return full_transcript.strip()

    @staticmethod
    def generate_srt(audio_path):
        chunks = AudioService.split_audio(audio_path)
        full_srt = ""
        for i, chunk in enumerate(chunks):
            with open(chunk, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio_file,
                    response_format="srt"
                )
            # Adjust timestamps for each chunk
            lines = response.split('\n')
            for j in range(1, len(lines), 4):
                if ' --> ' in lines[j]:
                    time_parts = lines[j].split(' --> ')
                    start_time = AudioService.adjust_time(time_parts[0], i * 60)
                    end_time = AudioService.adjust_time(time_parts[1], i * 60)
                    lines[j] = f"{start_time} --> {end_time}"
            full_srt += '\n'.join(lines) + '\n\n'
            os.remove(chunk)  # Clean up the chunk file
        return full_srt.strip()

    @staticmethod
    def adjust_time(time_str, seconds_to_add):
        time_str = time_str.replace(',', '.').strip()

        # Handle different time formats
        if ':' not in time_str:
            # Assume the time is in seconds
            total_seconds = float(time_str) + seconds_to_add
        else:
            parts = time_str.split(':')
            if len(parts) == 2:
                # Format: MM:SS.mmm
                m, s = parts
                total_seconds = int(m) * 60 + float(s) + seconds_to_add
            elif len(parts) == 3:
                # Format: HH:MM:SS.mmm
                h, m, s = parts
                total_seconds = int(h) * 3600 + int(m) * 60 + float(s) + seconds_to_add
            else:
                raise ValueError(f"Unexpected time format: {time_str}")

        # Convert total_seconds back to SRT time format
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')
