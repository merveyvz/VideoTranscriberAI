import os
import shlex
from pathlib import Path

import yt_dlp
import ffmpeg
import subprocess
from app.config import TEMP_DIR


def get_video_resolutions(url):
    ydl_opts = {
        'listformats': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info['formats']
        resolutions = set()
        for f in formats:
            if f.get('height'):
                resolutions.add(f'{f["height"]}p')
    return sorted(list(resolutions), key=lambda x: int(x[:-1]), reverse=True)


def download_video(url, resolution='best'):
    ydl_opts = {
        'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
        'format': f'bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]' if resolution != 'best' else 'bestvideo+bestaudio/best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename


def extract_audio(video_path):
    audio_path = os.path.join(TEMP_DIR, 'audio.wav')
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        raise Exception(f"Error extracting audio: {e.stderr.decode()}")
    return audio_path


def mux_subtitles(video_path, srt_path, output_path):
    try:
        # Validate input files
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        # Print file sizes for debugging
        print(f"Video file size: {os.path.getsize(video_path)} bytes")
        print(f"SRT file size: {os.path.getsize(srt_path)} bytes")

        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', srt_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-c:s', 'mov_text',
            '-metadata:s:s:0', 'language=eng',
            '-movflags', '+faststart',
            '-y',  # Overwrite output file if it exists
            output_path
        ]

        # Run ffmpeg command and capture output
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Print ffmpeg output for debugging
        print("FFmpeg stdout:", result.stdout)
        print("FFmpeg stderr:", result.stderr)

        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output video file was not created: {output_path}")

        return output_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed with return code {e.returncode}")
        print("FFmpeg stdout:", e.stdout)
        print("FFmpeg stderr:", e.stderr)
        raise Exception(f"Error muxing subtitles: {e.stderr}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise


def burn_subtitles(video_path, srt_path, output_path):
    try:
        # Convert to Path objects
        video_path = Path(video_path).resolve()
        srt_path = Path(srt_path).resolve()
        output_path = Path(output_path).resolve()

        # Validate input files
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not srt_path.exists():
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        # Print file sizes and paths for debugging
        print(f"Video file: {video_path}")
        print(f"Video file size: {video_path.stat().st_size} bytes")
        print(f"SRT file: {srt_path}")
        print(f"SRT file size: {srt_path.stat().st_size} bytes")

        # Prepare the FFmpeg command
        command = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(srt_path),
            '-filter_complex', f"[0:v][1:s]overlay[v]",
            '-map', "[v]",
            '-map', '0:a',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-movflags', '+faststart',
            '-y',  # Overwrite output file if it exists
            str(output_path)
        ]

        # Convert the command list to a string and properly escape it
        command_str = ' '.join(shlex.quote(str(arg)) for arg in command)

        # Run ffmpeg command and capture output
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True)

        # Print ffmpeg output for debugging
        print("FFmpeg command:", command_str)
        print("FFmpeg stdout:", result.stdout)
        print("FFmpeg stderr:", result.stderr)

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command_str, result.stdout, result.stderr)

        if not output_path.exists():
            raise FileNotFoundError(f"Output video file was not created: {output_path}")

        return str(output_path)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed with return code {e.returncode}")
        print("FFmpeg stdout:", e.stdout)
        print("FFmpeg stderr:", e.stderr)
        raise Exception(f"Error burning subtitles: {e.stderr}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise