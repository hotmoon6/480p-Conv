from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import ffmpeg
import requests

app = Flask(__name__)
app.config['CONVERTED_FOLDER'] = 'converted'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # Get the video URL from the form
    video_url = request.form.get('video_url')

    # Check if a video URL was provided
    if not video_url:
        return render_template('index.html', message='No video URL provided')

    # Download the video from the URL
    response = requests.get(video_url)
    if response.status_code != 200:
        return render_template('index.html', message='Failed to download video from the provided URL')

    # Save the downloaded video to a file
    filename = secure_filename('video.mp4')
    video_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
    with open(video_path, 'wb') as file:
        file.write(response.content)

    # Convert the video to 480p
    converted_filename = f"converted_{filename}"
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], converted_filename)
    ffmpeg.input(video_path).output(converted_path, vf='scale=854:480').run()

    # Provide the download link to the converted video
    return render_template('index.html', converted_file=converted_filename)

@app.route('/download/<path:filename>')
def download(filename):
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)

    # Check if the file exists
    if not os.path.isfile(converted_path):
        return render_template('index.html', message='File not found')

    # Send the file for download
    return send_file(converted_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
