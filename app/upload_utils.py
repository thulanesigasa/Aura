import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_secure_upload(file, upload_folder):
    """
    Sanitize filename and save file to the specified folder.
    Returns the saved filename if successful, None otherwise.
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Ensure unique filename to prevent overwriting
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(upload_folder, filename)):
            filename = f"{base}_{counter}{ext}"
            counter += 1
            
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return filename
    return None
