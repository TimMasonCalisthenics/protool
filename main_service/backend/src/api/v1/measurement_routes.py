from flask import Blueprint , request, Response
from flask_jwt_extended import jwt_required , get_jwt_identity
from api.utils.jsonRespon import json_response
from api.middleware.middlewares import role_required
from application.services.mea_service import MeasurementService
from infrastructure.repository.mea_repository import MeasurementRepository
from infrastructure.repository.product_repository import ProductRepository
from infrastructure.repository.MeasurementDraftSpec_repository import MeasurementDraftSpecRepository
from infrastructure.repository.MeasurementRawValue_repository import MeasurementRawValueRepository
from infrastructure.repository.setting_repository import SettingRepository
from application.dtos.measurementDTO import MeasurementCreate , MeasurementUpdate \
                                            , MeasurementResponse , MeasurementDraftCreate \
                                            , MeasurementDraftUpdate , MeasurementSaveDraft
from app import db
from flask import current_app

measurement_bp = Blueprint('measurement', __name__)
measurement_service = MeasurementService(MeasurementRepository(db) , ProductRepository(db) , MeasurementDraftSpecRepository(db) , MeasurementRawValueRepository(db) , SettingRepository(db))

@measurement_bp.route('', methods=['POST'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def save_measurement():
    # data = MeasurementCreate(**request.json)
    data = MeasurementCreate.model_validate(request.json)    
    measurement_service.create_measurement(data)
    return json_response(
        message="Save measurement successfully"
    )
    
@measurement_bp.route('/draft/reset_point', methods=['PATCH'])
@jwt_required()
@role_required('operator', 'supervisor', 'admin')
def reset_point():
    data = request.json
    measurement_service.reset_point_measurement(data['draft_id'], data['spec_point_id'])
    return json_response(message="Reset point successfully")

@measurement_bp.route('', methods=['GET'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def get_all_measurements():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    search = request.args.get('search', None)
    search_result = request.args.get('search_result', None)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    try:
        data , total = measurement_service.get_all_measurements_paginated(page , limit , search, search_result , start_date, end_date)
        return json_response(
            data ={'measurements':data , 'total_count':total},
            message="Get all measurements successfully"
        )
    except Exception as e:
        current_app.logger.error(e)
        return json_response(
            message="Get all measurements failed",
            status_code=500
        )

@measurement_bp.route('/export', methods=['GET'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def export_measurements_csv():
    search = request.args.get('search', None)
    search_result = request.args.get('search_result', None)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    try:
        csv_data = measurement_service.export_measurements_csv(search, search_result,start_date, end_date)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=measurements.csv"}
        )
    except Exception as e:
        current_app.logger.error(e)
        return json_response(
            message="Export measurements failed",
            status_code=500
        )

@measurement_bp.route('/<int:measurement_id>', methods=['GET'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def get_measurement_detail(measurement_id):

    data = measurement_service.get_measurement_by_id(measurement_id)
    return json_response(
        data = data,
        message="Get measurement detail successfully"
    )



@measurement_bp.route('/<int:measurement_id>', methods=['PATCH'])
@jwt_required()
@role_required('supervisor' , 'admin' )
def update_measurement(measurement_id):
    # data = MeasurementUpdate(**request.json)
    data = MeasurementUpdate.model_validate(request.json)    
    measurement_service.update_measurement(measurement_id , data)
    return json_response(
        data = data,
        message="Update measurement successfully"
    )

@measurement_bp.route('/<int:measurement_id>', methods=['DELETE'])
@jwt_required()
@role_required('supervisor' , 'admin')
def delete_measurement(measurement_id):
    measurement_service.delete_measurement(measurement_id)
    return json_response(
        message="Delete measurement successfully"
    )




@measurement_bp.route('/draft', methods=['POST'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def create_measurements_draft():
    try:
        data = MeasurementDraftCreate.model_validate(request.json)
        user_id = get_jwt_identity()
        data = measurement_service.create_measurements_draft(int(user_id) , data)
        dataResponse = MeasurementResponse.model_validate(data).model_dump(exclude_none=True)
        return json_response(
            data = dataResponse,
            message="Create measurements draft successfully"
        )
    except Exception as e:
        current_app.logger.error(e)
        return json_response(
            message="Create measurements draft failed",
            status_code=500
        )

@measurement_bp.route('/draft/<int:draft_id>', methods=['PATCH'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def update_measurements_draft(draft_id):
    # data = MeasurementDraftUpdate(**request.json)
    data = MeasurementDraftUpdate.model_validate(request.json)
    user_id = get_jwt_identity()
    data = measurement_service.update_measurements_draft(draft_id ,data)
    dataResponse = MeasurementResponse.model_validate(data).model_dump(exclude_none=True)
    return json_response(
        data = dataResponse,
        message="Update measurements draft successfully"
    )

@measurement_bp.route('/cancel_draft', methods=['PATCH'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def cancel_measurements_draft():
    try:
        data = measurement_service.cancel_measurements_draft()
        return json_response(
            message="Cancel measurements draft successfully"
        )
    except Exception as e:
        current_app.logger.error(e)
        return json_response(
            message="Cancel measurements draft failed",
            status_code=500
        )



@measurement_bp.route('/draft', methods=['GET'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def get_measurements_draft():
    try:
        # data ตอนนี้จะเป็น Dictionary ที่เราแกะมาจาก Service แล้ว
        data = measurement_service.get_measurements_draft()
        
        if data is None:
            return json_response(message="No draft found")
            
        # ✅ ส่ง data (dict) ออกไปตรงๆ เลย ไม่ต้องผ่าน Model Response อีกรอบ!
        return json_response(
            data=data, 
            message="Get measurements draft successfully"
        )
    except Exception as e:
        # ✅ เปลี่ยนจาก {str(e)} เป็น repr(e) เพื่อดู Error จริงใน Console
        current_app.logger.error(f"DEBUG: {repr(e)}") 
        return json_response(message=f"Error: {repr(e)}", status_code=500)


@measurement_bp.route('/save_draft', methods=['PATCH'])
@jwt_required()
@role_required('operator', 'supervisor' , 'admin')
def save_draft():    
    # data = MeasurementSaveDraft(**request.json)
    data = MeasurementSaveDraft.model_validate(request.json)
    measurement_service.save_draft(data.stage)
    return json_response(
        message="Save draft successfully"
    )
    