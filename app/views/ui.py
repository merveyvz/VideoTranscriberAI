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

    if process_button and not st.session_state.video_processed:
        if (upload_option == "Upload Video" and video_file) or (upload_option == "YouTube URL" and video_url):
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

        # Download button for original transcript
        st.download_button(
            label=f"Download Original Transcript",
            data=st.session_state.video_transcript,
            file_name=f"translation_original.txt",
            mime="text/plain"
        )

        if selected_languages:
            st.info("Translating to selected languages... This may take a moment.")

            translations = {}
            for lang in selected_languages:
                translated_text = translate_text(st.session_state.video_transcript, LANGUAGES[lang])
                translations[lang] = translated_text

                st.subheader(f"Translation ({lang})")
                st.text_area(f"{lang} Translation", translated_text, height=200)

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
                try:
                    for lang in srt_langs:
                        srt_content = create_srt(translations[lang], LANGUAGES[lang])
                        srt_filename = sanitize_filename(f"{video_title}_{lang}.srt")

                        srt_string = str(srt_content).encode('utf-8')

                        st.download_button(
                            label=f"Download {lang} SRT",
                            data=srt_string,
                            file_name=srt_filename,
                            mime="text/srt"
                        )

                    if upload_option == "YouTube URL":
                        try:
                            sanitized_video_title = sanitize_filename(video_title)
                            video_path = download_youtube_video(video_url, sanitized_video_title, format_id)
                            with open(video_path, "rb") as video_file:
                                st.download_button(
                                    label=f"Download Video ({selected_format})",
                                    data=video_file,
                                    file_name=os.path.basename(video_path),
                                    mime="video/mp4"
                                )
                            os.remove(video_path)
                        except Exception as e:
                            st.error(f"Error downloading video: {str(e)}")
                            st.info("You can still download the SRT files above.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

        else:
            st.info("Select target languages for translation.")
    elif process_button:
        st.error("Please upload a video file or enter a valid YouTube URL.")

