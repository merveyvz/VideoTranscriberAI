import streamlit as st
import os
from app.services import convert_video_to_audio, transcribe_audio, translate_text, download_youtube_video

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

    if 'video_transcript' not in st.session_state:
        st.session_state.video_transcript = None

    process_button = st.button("Process Video")

    if process_button:
        if (upload_option == "Upload Video" and video_file) or (upload_option == "YouTube URL" and video_url):
            st.session_state.video_transcript = None  # Reset transcript
            st.info("Processing video and transcribing... This may take a few minutes.")

            if upload_option == "Upload Video":
                # Save uploaded file temporarily
                temp_video_path = "temp_video.mp4"
                with open(temp_video_path, "wb") as f:
                    f.write(video_file.getbuffer())
                audio_path = convert_video_to_audio(temp_video_path)
            else:
                # Download YouTube video
                audio_path = download_youtube_video(video_url, "temp_audio")

            # Transcribe audio
            st.session_state.video_transcript = transcribe_audio(audio_path)

            # Clean up temporary files
            if upload_option == "Upload Video":
                os.remove(temp_video_path)
            os.remove(audio_path)

    if st.session_state.video_transcript:
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

            # Translate transcript
            for lang in selected_languages:
                translated_text = translate_text(st.session_state.video_transcript, LANGUAGES[lang])

                st.subheader(f"Translation ({lang})")
                st.text_area(f"{lang} Translation", translated_text, height=200)

                # Download button for each translation
                st.download_button(
                    label=f"Download {lang} Translation",
                    data=translated_text,
                    file_name=f"translation_{LANGUAGES[lang]}.txt",
                    mime="text/plain"
                )
        else:
            st.info("Select target languages for translation.")
    elif process_button:
        st.error("Please upload a video file or enter a valid YouTube URL.")
