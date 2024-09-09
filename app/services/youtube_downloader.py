
import yt_dlp
import os


def sanitize_filename(filename):
    return ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in filename).rstrip()


def get_video_info(url):
    ydl_opts = {'format': 'bestaudio/best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none']

        processed_formats = []
        for f in formats:
            if 'height' in f and f['height'] is not None:
                format_note = f"{f['height']}p"
                processed_formats.append((format_note, f['format_id']))

        processed_formats.sort(key=lambda x: int(x[0][:-1]), reverse=True)

        return sanitize_filename(info['title']), processed_formats


def download_youtube_video(url, output_path, format_id=None):
    ydl_opts = {
        'format': f'{format_id}/bestvideo+bestaudio/best' if format_id else 'bestvideo+bestaudio/best',
        'outtmpl': f'{output_path}.%(ext)s',
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            raise Exception(f"File not found after download: {filename}")

        return filename
    except Exception as e:
        raise Exception(f"Error downloading video: {str(e)}")