import asyncio
import logging
import os
import re

import streamlit as st
from app.services import AudioService, TranslationService, VideoService
from app.ui import create_language_container
from app.config import SUPPORTED_LANGUAGES, TEMP_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_css():
    with open(os.path.join("app\\ui", "styles.css")) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def is_valid_srt(content):
    pattern = re.compile(r'\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}\s*\n', re.MULTILINE)
    matches = pattern.findall(content)
    return len(matches) > 0


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


def main():
    st.set_page_config(page_title="Video Transcription and Translation App", layout="wide")
    load_css()
    st.title("Video Transcription and Translation App")

    if 'processed' not in st.session_state:
        st.session_state.processed = False
        st.session_state.video_path = None
        st.session_state.transcript = None
        st.session_state.srt_content = None
        st.session_state.translations = None

    video_source = st.radio("Choose video source:", ("YouTube URL", "Upload Video"))
    if video_source == "YouTube URL":
        video_url = st.text_input("Enter YouTube URL:")
    else:
        video_file = st.file_uploader("Upload video file", type=["mp4", "mov", "avi"])

    target_languages = st.multiselect("Select target languages for translation:", SUPPORTED_LANGUAGES)

    if st.button("Process Video") or st.session_state.processed:
        try:
            if not st.session_state.processed:
                with st.spinner("Processing video..."):
                    st.session_state.video_path, st.session_state.transcript, st.session_state.srt_content = process_video_with_progress(
                        video_source,
                        video_url if video_source == "YouTube URL" else None,
                        video_file if video_source == "Upload Video" else None
                    )
                    st.session_state.translations = TranslationService.translate_content(
                        st.session_state.transcript,
                        st.session_state.srt_content,
                        target_languages
                    )
                    st.session_state.processed = True

            st.subheader("Original Transcript")
            create_language_container("Original", st.session_state.transcript, st.session_state.srt_content)

            for lang, content in st.session_state.translations.items():
                create_language_container(lang, content["text"], content["srt"])

            st.subheader("Video")
            video_info = VideoService.get_video_info(st.session_state.video_path)

            # Display video thumbnail
            thumbnail_path = VideoService.generate_thumbnail(st.session_state.video_path)
            st.image(thumbnail_path, caption="Video Thumbnail")

            # Display video information
            st.write(f"Duration: {video_info['duration']} seconds")
            st.write(f"Resolution: {video_info['width']}x{video_info['height']}")
            st.write(f"Format: {video_info['format']}")

            # Download video button
            with open(st.session_state.video_path, "rb") as video_file:
                st.download_button(
                    label="Download Video",
                    data=video_file,
                    file_name="processed_video.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            logger.error(f"An error occurred in main: {str(e)}")
            if "FFmpeg is not installed" in str(e):
                st.error(
                    "FFmpeg is not installed or not accessible. Please install FFmpeg and add it to your system PATH.")
                st.error("You can download FFmpeg from: https://ffmpeg.org/download.html")
                st.error("After installation, you may need to restart your computer.")
            else:
                st.error(f"An error occurred: {str(e)}")
            st.error("Please check the application logs for more details and try again.")


if __name__ == "__main__":
    main()
