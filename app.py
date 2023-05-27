import os
import subprocess
import requests
from flask import Flask, render_template, request

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

app = Flask(__name__)

def download_video(url):
    response = requests.get(url, stream=True)
    file_name = 'input_video.mp4'  # Name of the downloaded video file
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    return file_name

def convert_video(input_file):
    output_file = 'output_video.mp4'  # Name of the converted video file
    command = ['ffmpeg', '-i', input_file, '-vf', 'scale=854:480', '-c:a', 'copy', output_file]
    subprocess.run(command, capture_output=True)
    return output_file

def upload_to_drive(file_path):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Create a new file on Google Drive
    file_drive = drive.CreateFile()

    # Set the title of the file
    file_drive['title'] = os.path.basename(file_path)

    # Set the content of the file
    file_drive.SetContentFile(file_path)

    # Upload the file to Google Drive
    file_drive.Upload()

    # Get the URL of the uploaded file
    return file_drive['alternateLink']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    video_url = request.form.get('video_url')

    # Download the video
    input_file = download_video(video_url)

    # Convert the video to 480p
    output_file = convert_video(input_file)

    # Upload the converted video to Google Drive and get the URL
    uploaded_url = upload_to_drive(output_file)

    # Clean up the temporary files
    os.remove(input_file)
    os.remove(output_file)

    # Render the result template with the uploaded URL
    return render_template('result.html', uploaded_url=uploaded_url)

if __name__ == '__main__':
    app.run()

