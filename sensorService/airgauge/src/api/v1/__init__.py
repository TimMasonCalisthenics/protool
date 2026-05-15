from flask import Blueprint
from .airgauge_routes import airgauge_bp



v1_bp = Blueprint('v1', __name__)
v1_bp.register_blueprint(airgauge_bp , url_prefix='/airgauge')