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
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
socketio = SocketIO(app)
app.logger.setLevel(logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_file_hash(file):
    hasher = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        hasher.update(chunk)
    file.seek(0)  # Reset file pointer
    return hasher.hexdigest()

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
        socketio.emit('progress', {'step': 'Bắt đầu xử lý', 'percentage': 0})
        
        file_hash = get_file_hash(file)
        filename = secure_filename(file_hash + os.path.splitext(file.filename)[1])
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        char_anno_dir = os.path.join(OUTPUT_FOLDER, file_hash)
        
        if os.path.exists(char_anno_dir):
            socketio.emit('progress', {'step': 'Sử dụng cache dữ liệu 3D của nhân vật đã xử lý trước đó', 'percentage': 30})
            app.logger.info(f"File {filename} đã tồn tại, sử dụng kết quả đã xử lý.")
        else:
            socketio.emit('progress', {'step': 'Xử lý ảnh mới', 'percentage': 10})
            os.makedirs(char_anno_dir, exist_ok=True)
            file.save(file_path)
            socketio.emit('progress', {'step': 'Tạo annotations', 'percentage': 20})
            image_to_annotations(file_path, char_anno_dir)
        
        socketio.emit('progress', {'step': 'Bắt đầu tạo animation', 'percentage': 40})
        retarget_cfg_fn = resource_filename(__name__, 'examples/config/retarget/fair1_ppf.yaml')
        start_time = time.time()
        annotations_to_animation(char_anno_dir, motion, retarget_cfg_fn)
        end_time = time.time()
        render_time = round(end_time - start_time, 2)
        
        socketio.emit('progress', {'step': 'Hoàn thành tạo animation', 'percentage': 90})
        
        output_gif_path = os.path.join(char_anno_dir, 'video.gif')
        if not os.path.exists(output_gif_path):
            return jsonify({'error': 'Không tìm thấy file output.gif'}), 404
        
        with open(output_gif_path, 'rb') as gif_file:
            gif_base64 = base64.b64encode(gif_file.read()).decode('ascii')
        
        socketio.emit('progress', {'step': 'Hoàn thành', 'percentage': 100})
        
        return jsonify({
            'gif': gif_base64,
            'message': 'GIF đã được tạo thành công',
            'render_time': render_time
        })
    except Exception as e:
        app.logger.error(f"Lỗi: {str(e)}")
        socketio.emit('progress', {'step': 'Lỗi xử lý', 'percentage': 100, 'error': str(e)})
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(filename=f'{log_dir}/log.txt', level=logging.DEBUG)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)