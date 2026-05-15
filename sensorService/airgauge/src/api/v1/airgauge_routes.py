import atexit
from flask import current_app
from flask import Blueprint, jsonify ,request

from api.utils.jsonRespon import json_response
from config.config_manager import cfg
from application.services.sensor_service import SensorService
from device_controller import IMBController
import os
airgauge_bp = Blueprint('airgauge', __name__)

sensor_service = None

def get_service():
    global sensor_service
    is_main_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not os.environ.get('FLASK_DEBUG')
    if sensor_service is None and is_main_process:
        print("Initializing Hardware Service inside Blueprint...")
        controller = IMBController()
        # controller.init_device("IMB_Test.ddk")
        controller.init_device()
        sensor_service = SensorService(controller, config=cfg)
        sensor_service.start()
        atexit.register(sensor_service.stop)
    
    return sensor_service

# เรียกใช้งานครั้งแรกตอนโหลดไฟล์
sensor_service = get_service()

#get sensor value
@airgauge_bp.route('/raw-value', methods=['GET'])
def get_raw_value_airgauge():
    data = sensor_service.get_sensorValue()
    return json_response(
        message="Get sensor successfully",
        data=data
    )
#get sensor value
@airgauge_bp.route('/value', methods=['GET'])
def get_airgauge():
    data = sensor_service.get_sensorValue()
    return json_response(
        message="Get sensor successfully",
        data=data
    )

@airgauge_bp.route('/', methods=['POST'])
def post_airgauge():
    return json_response(
        message="Post sensor successfully"
    )

#get and update setting airgauge
@airgauge_bp.route('/setting-airgauge', methods=['GET'])
def get_setting_airgauge():
    data = sensor_service.get_setting_airgauge()    
    return json_response(
        message="Get setting airgauge successfully",
        data = data
    )
@airgauge_bp.route('/setting-airgauge', methods=['PATCH'])
def update_setting_airgauge():
    new_data = request.json    
    data = sensor_service.set_setting_airgauge(new_data['key'] , new_data['value'])
    return json_response(
        message="Get setting airgauge successfully",
        data = data
    )
# all settings service
@airgauge_bp.route('/all-setting-airgauge', methods=['GET'])
def get_all_setting_airgauge():
    data = sensor_service.get_all_settings()
    return json_response(
        message="Get setting airgauge successfully",
        data = data
    )
@airgauge_bp.route('/all-setting-airgauge', methods=['PATCH'])
def update_all_setting_airgauge():
    new_data = request.json
    data = sensor_service.update_allConfig(new_data)
    return json_response(
        message="Get setting airgauge successfully",
        data = data
    )

#start/stop send value to main service
@airgauge_bp.route('/start-send', methods=['POST'])
def start_send():
    sensor_service.start_sending()
    return json_response(
        message="Start send successfully"
    )
@airgauge_bp.route('/stop-send', methods=['POST'])
def stop_send():
    sensor_service.stop_sending()
    return json_response(
        message="Stop send successfully"
    )
    
