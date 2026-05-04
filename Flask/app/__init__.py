from flask import Flask
from app.db.session import db
from app.auth_views import auth_bp
from app.views import ads_bp, register_error_handlers
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ads_bp)
    register_error_handlers(app)
    return app
