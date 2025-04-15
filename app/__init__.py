from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.controllers.request_controller import request_bp
    app.register_blueprint(request_bp)

    return app
