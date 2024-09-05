# app/views/ui.py
import streamlit as st
import os
from app.services.audio_converter import convert_video_to_audio
from app.services.transcriber import transcribe_audio
from app.services.translator import translate_text

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
        default=["English"]
    )

    # File upload
    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

    if 'english_transcript' not in st.session_state:
        st.session_state.english_transcript = None

    if video_file:
        if st.session_state.english_transcript is None:
            st.info("Processing video and transcribing to English... This may take a few minutes.")

            # Save uploaded file temporarily
            temp_video_path = "temp_video.mp4"
            with open(temp_video_path, "wb") as f:
                f.write(video_file.getbuffer())

            # Convert video to audio
            audio_path = convert_video_to_audio(temp_video_path)

            # Transcribe audio
            original_transcript = transcribe_audio(audio_path)

            # Ensure the transcript is in English
            st.session_state.english_transcript = translate_text(original_transcript, "en")

            # Clean up temporary files
            os.remove(temp_video_path)
            os.remove(audio_path)

        st.subheader("English Transcript")
        st.text_area("Transcript", st.session_state.english_transcript, height=200)

        if selected_languages:
            st.info("Translating to selected languages... This may take a moment.")

            # Translate transcript
            for lang in selected_languages:
                if LANGUAGES[lang] != "en":  # Translate if the language is not English
                    translated_text = translate_text(st.session_state.english_transcript, LANGUAGES[lang])
                else:
                    translated_text = st.session_state.english_transcript  # Use English transcript for English

                st.subheader(f"Translation ({lang})")
                st.text_area(f"{lang} Translation", translated_text, height=200)

                # Download button for each translation
                st.download_button(
                    label=f"Download {lang} Translation",
                    data=translated_text,
                    file_name=f"translation_{LANGUAGES[lang]}.txt",
                    mime="text/plain"
                )

    st.info(
        "Note: This application uses OpenAI's GPT-4 and Whisper models. Make sure you have a valid API key in the .env file.")

# The rest of the files remain the same