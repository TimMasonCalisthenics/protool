from flask import Blueprint , request
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt
from api.utils.jsonRespon import json_response
from app import db
from flask import current_app,Blueprint, request, jsonify
from application.services.system_service import SystemService
from infrastructure.repository.setting_repository import SettingRepository
from api.middleware.middlewares import role_required
from infrastructure.database.database import db
from infrastructure.persistence.models.system_settings import SystemSetting
from api.middleware.middlewares import role_required

system_bp = Blueprint('system', __name__)
system_service = SystemService(SettingRepository(db))

@system_bp.route('/active_product', methods=['PATCH'])
@jwt_required() # ต้องล็อกอินก่อน
@role_required('admin') # เฉพาะ Admin เท่านั้น

def update_active_product():
    try:
        product_id = request.json.get('product_id')
        system_service.update_active_id_product(product_id)
        return json_response(
            message="Update active product successfully"
        )
    except Exception as e:
        return json_response(
            message="Update active product failed",
            status_code=400
        )

@system_bp.route('/active_product', methods=['GET'])
def get_active_product():    
    data = system_service.get_active_id_product()
    if not data:
        return json_response(
            message="Get active product failed",
            status_code=404
        )
    return json_response(
        data=data.active_product_id,
        message="Get active product successfully"
    )
    
@system_bp.route("/settings", methods=["PATCH"]) # ตัด /api/v1 ออกเพราะปกติ Blueprint จะมี Prefix อยู่แล้ว
def update_system_settings():
    try:
        data = request.get_json()
        settings = db.session.query(SystemSetting).first()
        
        if not settings:
            return json_response(message="Settings not found", status_code=404)

        # อัปเดตค่าตาม Key ที่ส่งมา
        if "is_barcode_enabled" in data:
            settings.is_barcode_enabled = int(data["is_barcode_enabled"])
        if "is_mitutoyo_enabled" in data:
            settings.is_mitutoyo_enabled = int(data["is_mitutoyo_enabled"])
        if "is_airgauge_enabled" in data:
            settings.is_airgauge_enabled = int(data["is_airgauge_enabled"])

        db.session.commit()
        return json_response(message="Settings updated successfully")
    except Exception as e:
        db.session.rollback()
        return json_response(message=f"Update failed: {str(e)}", status_code=400)


@system_bp.route('/settings', methods=['GET'])
def get_system_settings():
    settings = db.session.query(SystemSetting).first()
    if not settings:
        return json_response(message="Settings not found", status_code=404)
    
    return json_response(
        data={
            "is_barcode_enabled": settings.is_barcode_enabled,
            "is_mitutoyo_enabled": settings.is_mitutoyo_enabled,
            "is_airgauge_enabled": settings.is_airgauge_enabled
        },
        message="Get settings successfully"
    )