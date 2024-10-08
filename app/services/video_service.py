import json
import logging
import os
import shutil
import subprocess
import yt_dlp
from app.config import TEMP_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoService:
    @staticmethod
    def check_ffmpeg():
        try:
            result = subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True, text=True)
            logger.info(f"FFmpeg version: {result.stdout.split('\\n')[0]}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg check failed: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("FFmpeg not found in system PATH")
            return False

    @staticmethod
    def download_video(url, progress_hook):
        ydl_opts = {
            'outtmpl': f'{TEMP_DIR}/%(id)s.%(ext)s',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return f"{TEMP_DIR}/{info['id']}.mp4"

    @staticmethod
    def extract_audio(video_path):
        try:
            audio_path = os.path.join(TEMP_DIR, f"{os.path.splitext(os.path.basename(video_path))[0]}.wav")
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                audio_path
            ]
            logger.info(f"Executing FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Expected audio file not found at {audio_path}")
            return audio_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise Exception(f"Failed to extract audio. FFmpeg error: {e.stderr}")
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise

    @staticmethod
    def generate_thumbnail(video_path):
        thumbnail_path = os.path.join(TEMP_DIR, 'thumbnail.jpg')
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:01.000',
            '-vframes', '1',
            thumbnail_path
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return thumbnail_path
