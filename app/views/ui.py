import base64
import io

import streamlit as st
import os
from app.services import convert_video_to_audio, transcribe_audio, translate_text, download_youtube_video, \
    get_video_info, create_srt, sanitize_filename

LANGUAGES = {
    "English": "en",
    "Turkish": "tr",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it"
}


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href


def render_ui():
    st.set_page_config(page_title="Video Translation App", layout="wide")
    st.title("Video Translation App")

    # Initialize session state
    if 'video_processed' not in st.session_state:
        st.session_state.video_processed = False
    if 'video_transcript' not in st.session_state:
        st.session_state.video_transcript = None
    if 'video_info' not in st.session_state:
        st.session_state.video_info = None
    if 'translations' not in st.session_state:
        st.session_state.translations = {}

    # Language selection
    selected_languages = st.multiselect(
        "Select target languages for translation",
        options=list(LANGUAGES.keys()),
    )

    # File upload or YouTube URL input
    upload_option = st.radio("Choose input method:", ("Upload Video", "YouTube URL"))

    if upload_option == "Upload Video":
        video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
    else:
        video_url = st.text_input("Enter YouTube video URL")

    process_button = st.button("Process Video")

    if process_button:
        st.session_state.video_processed = False
        st.session_state.video_transcript = None
        st.session_state.video_info = None
        st.session_state.translations = {}

    if process_button or (not st.session_state.video_processed and (
            (upload_option == "Upload Video" and video_file) or (upload_option == "YouTube URL" and video_url))):
        st.info("Processing video and transcribing... This may take a few minutes.")

        try:
            if upload_option == "Upload Video":
                temp_video_path = "temp_video.mp4"
                with open(temp_video_path, "wb") as f:
                    f.write(video_file.getbuffer())
                audio_path = convert_video_to_audio(temp_video_path)
                st.session_state.video_info = ("Uploaded Video", [("Original", "original")])
            else:
                st.session_state.video_info = get_video_info(video_url)
                audio_path = download_youtube_video(video_url, "temp_audio")

            st.session_state.video_transcript = transcribe_audio(audio_path)
            st.session_state.video_processed = True

            if upload_option == "Upload Video":
                os.remove(temp_video_path)
            os.remove(audio_path)

        except Exception as e:
            st.error(f"An error occurred while processing the video: {str(e)}")
            return

    if st.session_state.video_processed and st.session_state.video_transcript:
        st.subheader("Original Transcript")
        st.text_area("Transcript", st.session_state.video_transcript, height=200)

        if selected_languages:
            st.info("Translating to selected languages... This may take a moment.")

            for lang in selected_languages:
                if lang not in st.session_state.translations:
                    st.session_state.translations[lang] = translate_text(st.session_state.video_transcript,
                                                                         LANGUAGES[lang])

                st.subheader(f"Translation ({lang})")
                st.text_area(f"{lang} Translation", st.session_state.translations[lang], height=200)

            # SRT creation and download options
            st.subheader("Download Options")
            srt_langs = st.multiselect("Select languages for SRT files", options=selected_languages)

            if st.session_state.video_info:
                video_title, formats = st.session_state.video_info
                if upload_option == "YouTube URL":
                    selected_format = st.selectbox("Select video resolution", options=[f[0] for f in formats])
                    format_id = next(f[1] for f in formats if f[0] == selected_format)
                else:
                    format_id = None

            if st.button("Generate Downloads"):
                for lang in srt_langs:
                    # Generate the SRT content
                    srt_content = create_srt(st.session_state.translations[lang], LANGUAGES[lang])
                    srt_filename = sanitize_filename(f"{video_title}_{lang}.srt")

                    # Use an in-memory buffer to store the SRT content instead of a file
                    srt_buffer = io.StringIO(srt_content)

                    # Create a download button for each language
                    st.download_button(
                        label=f"Download {lang} SRT",
                        data=srt_buffer.getvalue(),  # Get the content of the buffer
                        file_name=srt_filename,
                        mime="text/srt"
                    )

                    # Close the buffer after use
                    srt_buffer.close()

                if upload_option == "YouTube URL":
                    try:
                        sanitized_video_title = sanitize_filename(video_title)
                        video_path = download_youtube_video(video_url, sanitized_video_title, format_id)
                        with open(video_path, "rb") as video_file:
                            st.download_button(
                                label=f"Download Video ({selected_format})",
                                data=video_file,
                                file_name=os.path.basename(video_path),
                                mime="video/mp4",
                                key="video_download"
                            )
                        os.remove(video_path)
                    except Exception as e:
                        st.error(f"Error downloading video: {str(e)}")
                        st.info("You can still download the SRT files above.")

        else:
            st.info("Select target languages for translation.")

    elif process_button:
        st.error("Please upload a video file or enter a valid YouTube URL.")