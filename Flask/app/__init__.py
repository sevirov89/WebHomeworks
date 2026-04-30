from flask import Flask
from app.db.session import db
from app.views import ads_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(ads_bp)
    return app
