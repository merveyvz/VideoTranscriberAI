import streamlit as st


def create_language_container(language, text, srt):
    with st.expander(f"{language} Translation"):
        st.text_area(f"{language} Transcript", text, height=150)
        st.download_button(f"Download {language} Transcript", text, f"{language.lower()}_transcript.txt")
        st.text_area(f"{language} SRT", srt, height=150)
        st.download_button(f"Download {language} SRT", srt, f"{language.lower()}_subtitles.srt")