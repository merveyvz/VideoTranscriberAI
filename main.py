import re
from pathlib import Path

import streamlit as st
import os
from app.config import SUPPORTED_LANGUAGES, TEMP_DIR
from app.services import (download_video, extract_audio, transcribe_audio, translate_text, create_srt,
                          translate_srt, mux_subtitles, get_video_resolutions, burn_subtitles)
from utils import save_uploaded_file

st.set_page_config(page_title="Video Translator", page_icon="🎥", layout="wide")
st.markdown('<style>' + open('static/styles.css').read() + '</style>', unsafe_allow_html=True)


def sanitize_filename(filename):
    return re.sub(r'[^\w\-_. ]', '_', filename)


def main():
    st.title("Video Translator")

    # Initialize session state
    if 'video_processed' not in st.session_state:
        st.session_state.video_processed = False
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'audio_path' not in st.session_state:
        st.session_state.audio_path = None
    if 'transcript' not in st.session_state:
        st.session_state.transcript = None
    if 'translations' not in st.session_state:
        st.session_state.translations = {}
    if 'original_srt' not in st.session_state:
        st.session_state.original_srt = None
    if 'youtube_url' not in st.session_state:
        st.session_state.youtube_url = None

    # Language selection
    selected_languages = st.multiselect("Select languages for translation", options=SUPPORTED_LANGUAGES)

    # Video input
    video_source = st.radio("Choose video source", ("Upload video", "YouTube URL"))

    if video_source == "Upload video":
        uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov'])
        if uploaded_file is not None:
            st.session_state.video_path = save_uploaded_file(uploaded_file)
    else:
        st.session_state.youtube_url = st.text_input("Enter YouTube URL")
        if st.session_state.youtube_url:
            resolutions = get_video_resolutions(st.session_state.youtube_url)
            selected_resolution = st.selectbox("Select video resolution", resolutions)

    if st.button("Process Video"):
        if st.session_state.video_path is not None or st.session_state.youtube_url:
            with st.spinner("Processing video..."):
                if video_source == "YouTube URL":
                    st.session_state.video_path = download_video(st.session_state.youtube_url, selected_resolution)

                # Extract audio
                st.session_state.audio_path = extract_audio(st.session_state.video_path)

                # Transcribe audio
                st.session_state.transcript = transcribe_audio(st.session_state.audio_path)

                # Translate transcript
                st.session_state.translations = {}
                for lang in selected_languages:
                    st.session_state.translations[lang] = translate_text(st.session_state.transcript, lang)

                # Generate original SRT
                st.session_state.original_srt = create_srt(st.session_state.audio_path)

                st.session_state.video_processed = True

    if st.session_state.video_processed:
        # Display results
        st.subheader("Original Transcript")
        st.text_area("Original Transcript", st.session_state.transcript, height=200)

        for lang, translation in st.session_state.translations.items():
            st.subheader(f"{lang} Translation")
            st.text_area(f"{lang} Translation", translation, height=200)

        # Download options
        st.subheader("Download Options")
        st.download_button("Download Original Transcript", st.session_state.transcript, "transcript.txt")
        for lang, translation in st.session_state.translations.items():
            st.download_button(f"Download {lang} Translation", translation, f"{lang.lower()}_translation.txt")

        # SRT download
        st.download_button("Download Original SRT", st.session_state.original_srt, "original_subtitles.srt")

        for lang in selected_languages:
            translated_srt = translate_srt(st.session_state.original_srt, lang)
            st.download_button(f"Download {lang} SRT", translated_srt, f"{lang.lower()}_subtitles.srt")

            st.subheader("Download Video with Subtitles")
            selected_lang_for_video = st.selectbox("Select language for video subtitles",
                                                   ["Original"] + list(st.session_state.translations.keys()))

            if st.button("Generate Video with Subtitles"):
                with st.spinner("Generating video with subtitles... This may take a few minutes."):
                    try:
                        if selected_lang_for_video == "Original":
                            srt_content = st.session_state.original_srt
                        else:
                            srt_content = translate_srt(st.session_state.original_srt, selected_lang_for_video)

                        if srt_content:
                            srt_filename = sanitize_filename(f"subtitles_{selected_lang_for_video}.srt")
                            srt_path = Path(TEMP_DIR) / srt_filename
                            srt_path.write_text(srt_content, encoding="utf-8")

                            st.text(f"SRT file created: {srt_path}")
                            st.text(f"SRT file size: {srt_path.stat().st_size} bytes")

                            output_filename = sanitize_filename(f"video_with_{selected_lang_for_video}_subtitles.mp4")
                            output_video_path = Path(TEMP_DIR) / output_filename
                            burn_subtitles(st.session_state.video_path, str(srt_path), str(output_video_path))

                            st.text(f"Output video created: {output_video_path}")
                            st.text(f"Output video size: {output_video_path.stat().st_size} bytes")

                            with output_video_path.open("rb") as f:
                                st.success(
                                    "Video processing complete! You can now download the video with burned-in subtitles.")
                                st.download_button(
                                    f"Download Video with {selected_lang_for_video} Subtitles",
                                    f,
                                    file_name=output_filename,
                                    mime="video/mp4"
                                )
                            st.info(
                                "The video has been processed with H.264 video codec and AAC audio codec. The subtitles have been burned directly into the video and should be visible on all players.")
                        else:
                            st.error("Failed to generate SRT content. Please try processing the video again.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.error("Please check the console for more detailed error information.")
                        st.error(
                            "If the problem persists, please ensure FFmpeg is correctly installed and supports libx264 and AAC encoding.")

                        # Print additional debugging information
                        st.text("Debugging Information:")
                        st.text(f"TEMP_DIR: {TEMP_DIR}")
                        st.text(f"Video path: {st.session_state.video_path}")
                        st.text(f"SRT path: {srt_path if 'srt_path' in locals() else 'Not created'}")
                        st.text(
                            f"Output video path: {output_video_path if 'output_video_path' in locals() else 'Not created'}")
                        st.text(f"Files in TEMP_DIR: {list(Path(TEMP_DIR).glob('*'))}")


if __name__ == "__main__":
    main()
