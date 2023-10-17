from flask import Flask, render_template, request, send_file, jsonify, session, Response
from pytube import YouTube
import requests
from tqdm import tqdm
from io import BytesIO
import secrets
import re


app = Flask(__name__)

# Secret key for session management
app.secret_key = secret_key = secrets.token_hex(32)

# Variable to track download progress
download_in_progress = False
download_progress = 0

# Function to download a video with a progress bar
def download_video_with_progress(url, format_choice):
    global download_progress  # Declare the variable as global
    download_progress = 0  # Set download progress to 0 at the start

    yt = YouTube(url)

    # Sanitize the video title to remove invalid characters for file names
    video_title = re.sub(r'[\/:*?"<>|]', '', yt.title)

    if format_choice == 'mp4':
        stream = yt.streams.get_highest_resolution()
        total_bytes = stream.filesize  # Get the total file size in bytes
        video_data = BytesIO()

        response = requests.get(stream.url, stream=True)
        with tqdm(total=total_bytes, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    video_data.write(chunk)
                    pbar.update(len(chunk))
                    download_progress = (video_data.tell() / total_bytes) * 100  # Update download progress

        video_data.seek(0)
        return video_data, f'{video_title}.mp4', 'video/mp4', total_bytes

    if format_choice == 'mp3':
        audio_stream = yt.streams.get_audio_only()
        total_bytes = audio_stream.filesize
        audio_data = BytesIO()

        response = requests.get(audio_stream.url, stream=True)
        with tqdm(total=total_bytes, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_data.write(chunk)
                    pbar.update(len(chunk))
                    download_progress = (audio_data.tell() / total_bytes) * 100

        audio_data.seek(0)
        return audio_data, f'{video_title}.mp3', 'video/mp3', total_bytes



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['GET'])
def download_file():
    global download_in_progress

    if request.method == 'GET':
        try:
            video_url = request.args.get('link')
            format_choice = request.args.get('format')

            video_data, filename, mimetype, total_bytes = download_video_with_progress(video_url, format_choice)

            def generate():
                with tqdm(total=total_bytes, unit='B', unit_scale=True) as pbar:
                    for chunk in video_data:
                        yield chunk
                        pbar.update(len(chunk))

            download_in_progress = False
            return Response(generate(), content_type=mimetype, headers={"Content-Disposition": f"attachment; filename={filename}"})
        except Exception as e:
            error_code = str(e)
            if "regex_search" in str(e):
                error_code = "500 (you probably entered an invalid link)"  # Fix the assignment operator here
            error_image_url = "https://files.catbox.moe/eq311s.png"
            return render_template('error.html', error_code=error_code, error_image_url=error_image_url)

@app.route('/progress', methods=['GET'])
def get_progress():
    global download_progress  # Declare the variable as global
    return jsonify({"progress": download_progress})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
