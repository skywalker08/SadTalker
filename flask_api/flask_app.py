from flask import Flask, request, jsonify, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from .sadtalker_service import SadTalkerService

def create_app():
    app = Flask(__name__)

    # Configure upload folder
    UPLOAD_FOLDER = 'uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    

    @app.route('/generate-video', methods=['POST'])
    def generate_video():
        print('Request received')
        print(request.files)
        if 'image' not in request.files or 'audio' not in request.files:
            return jsonify({'error': 'Image and audio files are required'}), 400

        video_name = request.form['video_name']
        image_file = request.files['image']
        audio_file = request.files['audio']
        abs_path = os.path.abspath('results/')
        if os.path.exists(abs_path/Path(video_name+'.mp4')):
            result = url_for('results', filename=video_name+'.mp4', _external=True)
            print(result)
            return jsonify({'status': 'success', 'result_video': result}), 200

        image_filename = secure_filename(image_file.filename)  # secure_filename is used to prevent directory traversal attacks
        audio_filename = secure_filename(audio_file.filename)

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

        image_file.save(image_path)
        audio_file.save(audio_path)

        service = SadTalkerService(image_path, audio_path, video_name)
        try:
            result_video_path = service.generate_video()
            # create url for the generated video
            result = url_for('results', filename=video_name+'.mp4', _external=True)
            print(result)
            return jsonify({'status': 'success', 'result_video': result}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500
    
    @app.route('/results/<filename>')
    def results(filename):

        abs_path = os.path.abspath('results/')
        print(f'Sending file from {abs_path}')
        return send_from_directory(abs_path, filename)

    return app
