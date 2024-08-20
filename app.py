import io
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template
import os
import uuid
import cv2
import numpy as np
import requests
import json
import yaml
import base64
from pkg_resources import resource_filename
from examples.image_to_annotations import image_to_annotations
from examples.annotations_to_animation import annotations_to_animation
import time
from flask_socketio import SocketIO, emit
import animated_drawings.render

app = Flask(__name__)
socketio = SocketIO(app)
app.logger.setLevel(logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file nào được tải lên'}), 400
    
    file = request.files['file']
    motion = request.form.get('motion', 'examples/config/motion/dab.yaml')
    
    if file.filename == '':
        return jsonify({'error': 'Không có file nào được chọn'}), 400
    
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'error': 'Chỉ chấp nhận file ảnh (PNG, JPG, JPEG, GIF)'}), 400
    
    try:
        start_time = time.time()
        filename = str(uuid.uuid4()) + '.png'
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        char_anno_dir = os.path.join(OUTPUT_FOLDER, str(uuid.uuid4()))
        os.makedirs(char_anno_dir, exist_ok=True)
        
        socketio.emit('progress', {'status': 'Đang tạo annotations...', 'progress': 25})
        image_to_annotations(file_path, char_anno_dir)
        
        retarget_cfg_fn = resource_filename(__name__, 'examples/config/retarget/fair1_ppf.yaml')
        
        socketio.emit('progress', {'status': 'Đang tạo cấu hình MVC...', 'progress': 50})
        mvc_cfg = {
            'scene': {
                'ANIMATED_CHARACTERS': [{
                    'character_cfg': os.path.join(char_anno_dir, 'char_cfg.yaml'),
                    'motion_cfg': motion,
                    'retarget_cfg': retarget_cfg_fn
                }]
            },
            'view': {
                'USE_MESA': True
            },
            'controller': {
                'MODE': 'video_render',
                'OUTPUT_VIDEO_PATH': os.path.join(char_anno_dir, 'video.gif')
            }
        }
        
        mvc_cfg_path = os.path.join(char_anno_dir, 'mvc_cfg.yaml')
        with open(mvc_cfg_path, 'w') as f:
            yaml.dump(mvc_cfg, f)
        
        socketio.emit('progress', {'status': 'Đang tạo hoạt ảnh...', 'progress': 75})
        animated_drawings.render.start(mvc_cfg_path)
        
        output_gif_path = os.path.join(char_anno_dir, 'video.gif')
        if os.path.exists(output_gif_path) and os.path.getsize(output_gif_path) > 0:
            with open(output_gif_path, 'rb') as gif_file:
                gif_content = gif_file.read()
                if gif_content:
                    gif_base64 = base64.b64encode(gif_content).decode('ascii')
                    end_time = time.time()
                    render_time = round(end_time - start_time, 2)
                    socketio.emit('progress', {'status': 'Hoàn thành!', 'progress': 100})
                    return jsonify({
                        'gif': gif_base64,
                        'message': 'GIF đã được tạo thành công',
                        'render_time': render_time
                    })
                else:
                    return jsonify({'error': 'File GIF rỗng'}), 500
        else:
            return jsonify({'error': 'Không tìm thấy file output.gif hoặc file rỗng'}), 404
    except Exception as e:
        app.logger.error(f"Lỗi: {str(e)}", exc_info=True)
        return jsonify({'error': f'Đã xảy ra lỗi: {str(e)}'}), 500

if __name__ == '__main__':
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)