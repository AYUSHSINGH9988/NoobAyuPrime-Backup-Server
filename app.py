import os
from flask import Flask, request, send_from_directory, jsonify

app = Flask(__name__)

# 🟢 THE HACK: Har cloud server '/tmp' folder me write permission deta hai
BACKUP_DIR = "/tmp/backup_vault"
os.makedirs(BACKUP_DIR, exist_ok=True)

# 🔐 SECURITY
SECRET_KEY = "ayuprime_god_mode_123"

def is_authorized(req):
    return req.headers.get("x-api-key") == SECRET_KEY

# Home Route
@app.route('/', methods=['GET'])
def home():
    return "✅ Ayuprime Backup Vault is Online (Running from /tmp)!", 200

# 1. UPLOAD ENDPOINT
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if not is_authorized(request):
            return jsonify({"error": "Unauthorized"}), 401
        
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        original_path = request.headers.get('x-original-path', file.filename)
        
        save_path = os.path.join(BACKUP_DIR, original_path.lstrip('/'))
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        file.save(save_path)
        return jsonify({"status": "success", "saved_at": original_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. DOWNLOAD ENDPOINT
@app.route('/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    if not is_authorized(request):
        return "Unauthorized", 401
    try:
        return send_from_directory(BACKUP_DIR, filepath)
    except Exception as e:
        return str(e), 404

# 3. LIST ENDPOINT
@app.route('/list', methods=['GET'])
def list_files():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        files = []
        for root, _, filenames in os.walk(BACKUP_DIR):
            for f in filenames:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, BACKUP_DIR)
                files.append(rel_path.replace("\\", "/"))
                
        return jsonify({"total": len(files), "files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
