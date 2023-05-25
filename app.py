from flask import Flask, render_template, request, jsonify
import requests
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    video_url = request.json['videoUrl']
    video_filename = 'input.mp4'
    converted_filename = 'output.mp4'

    try:
        # Download the video
        response = requests.get(video_url)
        with open(video_filename, 'wb') as file:
            file.write(response.content)

        # Convert the video
        subprocess.call(['ffmpeg', '-i', video_filename, '-vf', 'scale=-2:480', '-c:a', 'copy', converted_filename])

        # Return the download link
        download_url = '/' + converted_filename
        return jsonify({'downloadUrl': download_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()


