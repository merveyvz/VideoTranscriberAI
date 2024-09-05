import ffmpeg


def convert_video_to_audio(video_path):
    audio_path = "temp_audio.mp3"
    stream = ffmpeg.input(video_path)
    stream = ffmpeg.output(stream, audio_path)
    ffmpeg.run(stream, overwrite_output=True)
    return audio_path
