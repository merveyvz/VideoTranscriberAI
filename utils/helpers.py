import logging
import os
import re
import shutil

import streamlit as st

from app.config import TEMP_DIR
from app.services import AudioService, VideoService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_progress_hook(d):
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            progress = int(float(d['downloaded_bytes']) / float(d['total_bytes']) * 100)
            st.session_state.download_progress.progress(progress)
            st.session_state.download_text.text(f"Downloading: {progress}% complete")
        else:
            downloaded = d['downloaded_bytes'] / (1024 * 1024)
            speed = d.get('speed', 0) / (1024 * 1024)
            st.session_state.download_text.text(f"Downloading: {downloaded:.1f}MB at {speed:.1f}MB/s")
    elif d['status'] == 'finished':
        st.session_state.download_text.text("Download completed. Processing video...")


def process_video_with_progress(video_source, video_url=None, video_file=None):
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        if not VideoService.check_ffmpeg():
            raise RuntimeError("FFmpeg is not installed or not accessible in the system PATH.")

        status_text.text("Downloading/Processing video...")
        if video_source == "YouTube URL":
            st.session_state.download_progress = st.progress(0)
            st.session_state.download_text = st.empty()
            video_path = VideoService.download_video(video_url, download_progress_hook)
            st.session_state.download_progress.empty()
            st.session_state.download_text.empty()
        else:
            video_path = os.path.join("temp", video_file.name)
            with open(video_path, "wb") as f:
                f.write(video_file.getbuffer())
        progress_bar.progress(20)

        status_text.text("Extracting audio...")
        audio_path = VideoService.extract_audio(video_path)
        progress_bar.progress(40)

        status_text.text("Transcribing audio...")
        transcript = AudioService.transcribe_audio(audio_path)
        progress_bar.progress(60)

        status_text.text("Generating SRT...")
        srt_content = AudioService.generate_srt(audio_path)
        progress_bar.progress(80)

        status_text.text("Finalizing...")
        os.remove(audio_path)
        progress_bar.progress(100)
        status_text.text("Processing complete!")

        return video_path, transcript, srt_content
    except Exception as e:
        logger.error(f"Error in process_video_with_progress: {str(e)}")
        raise


def load_css():
    with open(os.path.join("app\\ui", "styles.css")) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def reset_state():
    # Clear all session state variables
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Clear all files in the temp directory
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f'Failed to delete {file_path}. Reason: {e}')

    # Reinitialize session state to default values
    st.session_state.processed = False
    st.session_state.video_path = None
    st.session_state.transcript = None
    st.session_state.srt_content = None
    st.session_state.translations = {}
    st.session_state.video_source = "YouTube URL"
    st.session_state.video_url = ""
    st.session_state.target_languages = []
    st.session_state.thumbnail_path = None
    st.session_state.video_info = None
