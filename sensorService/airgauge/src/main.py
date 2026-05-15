import os
import sys
from flask import Flask
from api.v1 import v1_bp
from flask_cors import CORS
from waitress import serve 


def create_app():

    app = Flask(__name__)    
    CORS(app)    
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    return app

if __name__ == "__main__":
    app = create_app()
    is_compiled = hasattr(sys, "frozen") or hasattr(sys, "__compiled__") or sys.argv[0].endswith(".exe")

    if is_compiled:
        print("Running in compiled mode")
        serve(app, host='0.0.0.0', port=5001 ,threads=1)
    else:
        print("Running in debug mode")
        app.run(host='0.0.0.0', port=5001, debug=True , use_reloader=False)
