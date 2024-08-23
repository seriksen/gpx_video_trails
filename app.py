from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # Example video file path and duration
    video_path = 'gpx_animation.mp4'
    video_duration = 300  # Example duration in seconds
    return render_template('crop.html', video_path=video_path, video_duration=video_duration)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/crop', methods=['POST'])
def crop():
    start_time = request.form.get('start')
    end_time = request.form.get('end')
    video_path = request.form.get('video_path')

    # Implement cropping logic here
    # For example: using moviepy or FFmpeg to process the video

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
