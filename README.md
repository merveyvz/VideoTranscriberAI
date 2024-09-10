# Video Transcription and Translation App

## Overview

This Streamlit-based web application allows users to transcribe and translate video content from YouTube URLs or uploaded video files. It utilizes OpenAI's Whisper model for transcription and GPT model for translation, providing a user-friendly interface for processing videos and generating multilingual subtitles.

## Features

- Support for YouTube videos and local video file uploads
- YouTube video download using yt-dlp
- Audio extraction and transcription using OpenAI's Whisper model
- Translation of transcripts and subtitles into multiple languages
- Generation of SRT (SubRip Subtitle) files
- Download options for transcripts, SRT files, and processed videos
- Real-time progress tracking for video processing
- Thumbnail generation for processed videos

## Prerequisites

- Python 3.7+
- FFmpeg installed and accessible in the system PATH

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/merveyvz/VideoTranscriberAI.git
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

1. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Choose your video source (YouTube URL or file upload) and enter the URL or upload a file.

4. Click "Process Video" to start transcription.

5. Select target languages for translation and click "Translate" to generate translations.

6. Use the download buttons to save transcripts, SRT files, and the processed video.

## Project Structure

- `main.py`: The main Streamlit application
- `app/`
  - `services/`: Contains service classes for video, audio, and translation processing
  - `ui/`: UI components and styles
  - `config.py`: Configuration settings
- `utils.py`: Utility functions
- `requirements.txt`: List of Python dependencies


## Key Technologies

- **Streamlit**: Used for creating the web application interface.
- **OpenAI Whisper**: Employed for accurate audio transcription.
- **OpenAI GPT**: Utilized for high-quality text translation.
- **yt-dlp**: A YouTube video downloader, fork of youtube-dl with additional features and fixes. It's used in this project to download YouTube videos for processing.
- **FFmpeg**: Used for audio extraction and video processing tasks.