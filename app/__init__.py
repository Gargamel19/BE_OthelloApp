from flask import Flask
from flask_cors import CORS, cross_origin
import os

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

from app.extentions import db


def create_app(type="run"):
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    
    app.chat_reader_player = []
    app.recent_votes = {}

    app.config['SECRET_KEY'] = 'your_strong_secret_key'
    app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']

    jwt = JWTManager(app)

    if type == "test":
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_db.sqlite'
        app.config['TESTING'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    from app.user import user_bp
    app.register_blueprint(user_bp)
    
    from app.calender import calender_bp
    app.register_blueprint(calender_bp)

    from app.commands import create_tables, add_testdata
    app.cli.add_command(create_tables)
    app.cli.add_command(add_testdata)

    from app import models

    return app