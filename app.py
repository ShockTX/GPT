
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import os, mimetypes

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # ~1GB

ALLOWED_EXTENSIONS = {
    'mp3','wav','ogg','m4a','aac','flac','opus','webm',
    'mp4','m4v','mov','webm','ogv','avi','mkv'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(f.filename):
        return jsonify({'error': 'Unsupported file extension'}), 400
    filename = secure_filename(f.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    base, ext = os.path.splitext(filename)
    count = 1
    while os.path.exists(save_path):
        filename = f"{base}_{count}{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        count += 1
    f.save(save_path)
    return jsonify({'ok': True, 'filename': filename})

@app.route('/api/files')
def list_files():
    items = []
    for name in sorted(os.listdir(UPLOAD_FOLDER)):
        path = os.path.join(UPLOAD_FOLDER, name)
        if os.path.isfile(path):
            mime, _ = mimetypes.guess_type(name)
            items.append({'name': name, 'url': f'/uploads/{name}', 'mime': mime or 'application/octet-stream'})
    return jsonify(items)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    safe = os.path.basename(filename)
    path = os.path.join(UPLOAD_FOLDER, safe)
    if not os.path.isfile(path):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, safe, as_attachment=False)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
