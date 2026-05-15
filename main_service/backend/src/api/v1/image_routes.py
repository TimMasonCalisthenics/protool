import os
from flask import Blueprint, send_from_directory, current_app
from werkzeug.exceptions import NotFound
from api.utils.jsonRespon import json_response

image_bp = Blueprint('image', __name__)

@image_bp.route('/static/uploads/points/<string:filename>', methods=['GET'])
def upload_image_points(filename):    
    try:
        # ใช้ current_app.root_path เพื่อระบุตำแหน่งเริ่มต้นของโปรเจกต์ให้เป๊ะ
        directory = os.path.join(current_app.root_path, 'static', 'uploads', 'points')
        return send_from_directory(directory, filename)
    except NotFound:
        return json_response(message="Image not found", status_code=404)
    except Exception as e:
        return json_response(message=str(e), status_code=500)

@image_bp.route('/static/uploads/products/<string:filename>', methods=['GET'])
def upload_image(filename):    
    try:
        # ใช้ current_app.root_path เพื่อระบุตำแหน่งเริ่มต้นของโปรเจกต์ให้เป๊ะ
        directory = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
        return send_from_directory(directory, filename)
    except NotFound:
        return json_response(message="Image not found", status_code=404)
    except Exception as e:
        return json_response(message=str(e), status_code=500)