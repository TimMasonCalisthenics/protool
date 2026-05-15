from flask import Blueprint , request
from flask_jwt_extended import jwt_required , get_jwt_identity
from pydantic import TypeAdapter
from typing import List
from api.utils.jsonRespon import json_response
from api.middleware.middlewares import role_required

from application.services.mea_draft_service import MeasurementDraftService
from application.dtos.measurement_draft_DTO import MeasurementDraftDTO , MeasurementDraftResponse

from infrastructure.repository.mea_repository import MeasurementRepository
from infrastructure.repository.MeasurementDraftSpec_repository import MeasurementDraftSpecRepository
from infrastructure.repository.MeasurementRawValue_repository import MeasurementRawValueRepository
from infrastructure.repository.setting_repository import SettingRepository
from infrastructure.persistence.models.measurement_model import MeasurementModel, MeasurementDraftSpec
from flask import current_app
from app import db

measurement_draft_bp = Blueprint('measurement_draft', __name__)
measurement_draft_service = MeasurementDraftService(MeasurementRepository(db)
                                                    , MeasurementDraftSpecRepository(db)
                                                    , MeasurementRawValueRepository(db)
                                                    , SettingRepository(db))

# measurement_draft_routes.py
@measurement_draft_bp.route('', methods=['GET'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def get_measurement_draft():
    try:
        draft = db.session.query(MeasurementModel).filter_by(status='draft').first()
        if not draft:
            return json_response(data={"measurement_draft_specs": []}, message="No draft found")
            
        # ✅ แกะเป็น Dict เพื่อเลี่ยง Validation Error
        specs_list = [s.to_dict() for s in draft.measurement_draft_specs]

        return json_response(
            data={
                "id": draft.id,
                "serial_a": draft.serial_a,
                "measurement_draft_specs": specs_list
            },
            message="Get measurements draft successfully"
        )
    except Exception as e:
        current_app.logger.error(f"DEBUG: {repr(e)}")
        return json_response(message=f"Error: {repr(e)}", status_code=500)
    
@measurement_draft_bp.route('/clear-ng', methods=['PATCH'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def clear_measurement_draft_ng_value():    
    data = measurement_draft_service.clear_ng_value_measurement_draft()    
    return json_response(        
        message="Clear ng value measurement draft successfully"
    )
    

@measurement_draft_bp.route('/clear-ng-raw', methods=['PATCH'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def clear_measurement_draft_ng_and_raw_value():
    
    data = measurement_draft_service.clear_ng_and_raw_value_measurement_draft()    
    return json_response(        
        message="Clear ng and raw value measurement draft successfully"
    )
