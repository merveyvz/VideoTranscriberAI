import streamlit as st
from app.views.ui import render_ui
from app.config import load_config


def main():
    load_config()
    render_ui()


if __name__ == "__main__":
    main()
