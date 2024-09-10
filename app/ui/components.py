import streamlit as st


def create_language_container(language, text, srt):
    with st.expander(f"{language} Translation"):
        st.text_area("Translated Text", text, height=200, key=f"{language}_text")
        st.download_button(f"Download {language} Transcript", text, f"{language.lower()}_transcript.txt")
        st.text_area("SRT Content", srt, height=200, key=f"{language}_srt")
        st.download_button(f"Download {language} SRT", srt, f"{language.lower()}_subtitles.srt")

