import logging

import streamlit as st

from app.config import SUPPORTED_LANGUAGES
from app.services import TranslationService, VideoService
from app.ui import create_language_container
from utils import process_video_with_progress, reset_state, load_css

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    st.set_page_config(page_title="Video Transcription and Translation App", layout="wide")
    load_css()
    st.title("Video Transcription and Translation App")

    if 'processed' not in st.session_state:
        reset_state()

    row1, row2 = st.columns(2, vertical_alignment="bottom")
    with row1:
        video_source = st.radio("Choose video source:", ("YouTube URL", "Upload Video"),
                            key="video_source")
    with row2:
        if st.button("Reset"):
            reset_state()
            st.rerun()

    if video_source == "YouTube URL":
        video_url = st.text_input(label="Enter YouTube URL:", key="video_url", placeholder="https://www.youtube.com/...")
    else:
        video_file = st.file_uploader("Upload video file", type=["mp4", "mov", "avi"])
    process_button = st.button("Process Video")

    if process_button and not st.session_state.processed:
        try:
            st.session_state.video_path, st.session_state.transcript, st.session_state.srt_content = process_video_with_progress(
                video_source,
                video_url if video_source == "YouTube URL" else None,
                video_file if video_source == "Upload Video" else None
            )
            st.session_state.processed = True
            st.session_state.thumbnail_path = VideoService.generate_thumbnail(st.session_state.video_path)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please check the application logs for more details and try again.")

    target_languages = st.multiselect("Select target languages for translation:", SUPPORTED_LANGUAGES, key="target_languages")
    translation_button = st.button("Translate")

    if translation_button:
        with st.spinner("Translating..."):
            new_languages = [lang for lang in target_languages if lang not in st.session_state.translations]
            if new_languages:
                new_translations = TranslationService.translate_content(
                    st.session_state.transcript,
                    st.session_state.srt_content,
                    new_languages
                )
                st.session_state.translations.update(new_translations)

            languages_to_remove = set(st.session_state.translations.keys()) - set(target_languages)
            for lang in languages_to_remove:
                del st.session_state.translations[lang]

    for lang, content in st.session_state.translations.items():
        create_language_container(lang, content["text"], content["srt"])

    if st.session_state.processed:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Video")
            if st.session_state.thumbnail_path:
                st.image(st.session_state.thumbnail_path, width=300)
            if video_source == "YouTube URL" and st.session_state.video_path:
                with open(st.session_state.video_path, "rb") as video_file:
                    st.download_button(
                        label="Download Video",
                        data=video_file,
                        file_name="processed_video.mp4",
                        mime="video/mp4"
                    )

        with col2:
            st.subheader("Original Transcript")
            st.text_area("Transcript", st.session_state.transcript, height=150)
            st.download_button("Download Transcript", st.session_state.transcript, "transcript.txt")
            st.text_area("SRT", st.session_state.srt_content, height=150)
            st.download_button("Download SRT", st.session_state.srt_content, "subtitles.srt")


if __name__ == "__main__":
    main()
