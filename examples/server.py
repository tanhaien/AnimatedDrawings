from flask import Flask, request, send_file, render_template, jsonify
import os
from pathlib import Path
import uuid
import time
from image_to_annotations import image_to_annotations
from annotations_to_animation import annotations_to_animation
import hashlib
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn kích thước tải lên 16MB

# Tạo thư mục outputs nếu chưa tồn tại
OUTPUTS_DIR = Path('outputs')
OUTPUTS_DIR.mkdir(exist_ok=True)

# Tạo một thread pool để xử lý các tác vụ nặng
executor = ThreadPoolExecutor(max_workers=20)

# Tạo một lock để đồng bộ hóa truy cập vào tài nguyên dùng chung
file_lock = threading.Lock()

def get_file_hash(file):
    hasher = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        hasher.update(chunk)
    file.seek(0)  # Đặt lại con trỏ file
    return hasher.hexdigest()

def resize_image(image, size=(300, 300)):
    # Đọc ảnh từ file
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    image.seek(0)  # Đặt lại con trỏ file
    
    # Resize ảnh
    resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    
    # Chuyển đổi ảnh thành bytes
    _, img_encoded = cv2.imencode('.png', resized)
    return img_encoded.tobytes()

@app.route('/')
def index():
    return render_template('index.html')

def process_animation(annotations_dir):
    motion_cfg_fn = 'config/motion/dab.yaml'
    retarget_cfg_fn = 'config/retarget/fair1_ppf.yaml'
    
    start_time = time.time()
    annotations_to_animation(annotations_dir, motion_cfg_fn, retarget_cfg_fn)
    end_time = time.time()
    
    return end_time - start_time

@app.route('/render_gif', methods=['POST'])
def render_gif():
    if 'image' not in request.files:
        return 'Không có file ảnh nào được gửi', 400
    
    image = request.files['image']
    resized_image = resize_image(image)
    file_hash = hashlib.md5(resized_image).hexdigest()
    
    output_dir = OUTPUTS_DIR / file_hash
    output_dir.mkdir(exist_ok=True)
    
    image_path = output_dir / 'input_image.png'
    annotations_dir = output_dir / 'annotations'
    
    with file_lock:
        if not image_path.exists():
            with open(str(image_path), 'wb') as f:
                f.write(resized_image)
            image_to_annotations(str(image_path), str(annotations_dir))
    
    # Sử dụng thread pool để xử lý tác vụ nặng
    future = executor.submit(process_animation, str(annotations_dir))
    
    # Đợi kết quả từ thread pool
    render_time = future.result()
    
    return jsonify({
        'render_time': f'{render_time:.2f}',
        'gif_url': f'/get_gif/{file_hash}'
    })

@app.route('/get_gif/<path:file_hash>')
def get_gif(file_hash):
    gif_path = OUTPUTS_DIR / file_hash / 'annotations' / 'video.gif'
    return send_file(str(gif_path), mimetype='image/gif')

if __name__ == '__main__':
    app.run(debug=True)