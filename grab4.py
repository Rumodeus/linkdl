from io import BytesIO

from flask import Flask, render_template, request, send_file, jsonify
from pytube import YouTube

app = Flask(__name__)

@app.route('/embed', methods=['GET'])
def generate_embed():
    embed_data = {
        "embeds": [
            {
                "title": "Rikka's Youtube Downloader",
                "description": "hiiiiiiii",
                "image": {
                    "url": "https://files.catbox.moe/ahrytx.png"
                }
            }
        ]
    }
    return jsonify(embed_data)

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/download', methods=['GET'])
def download_file():
  if request.method == 'GET':
    video_url = request.args.get('link')
    format_choice = request.args.get('format')

    yt = YouTube(video_url)

    if format_choice == 'mp4':
      stream = yt.streams.get_highest_resolution()
      video_data = BytesIO()
      stream.stream_to_buffer(video_data)
      video_data.seek(0)

      return send_file(video_data,
                       as_attachment=True,
                       download_name=f'{yt.title}.mp4',
                       mimetype='video/mp4')
    elif format_choice == 'mp3':
      audio_stream = yt.streams.filter(only_audio=True).first()
      audio_data = BytesIO()
      audio_stream.stream_to_buffer(audio_data)
      audio_data.seek(0)

      return send_file(audio_data,
                       as_attachment=True,
                       download_name=f'{yt.title}.mp3',
                       mimetype='audio/mp3')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
