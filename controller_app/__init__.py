"""app to control the setting of algorithm module of 3CF project
"""
from flask import Flask
from .database import db
from .factory import factory_bp
from .workstation import workstation_bp
from .worker import worker_bp
from .face import face_bp
from .equipment_model import model_bp


def create_app(db_uri: str):
    """
    create flask application
    :param db_uri: database uri to use
    :return: flask app
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "\xea\x1e\xc2\x94\xec\xd9\xbf \x0flsG\xf6\xb5 \xa2~\x8c\x82\x17*\xfc{V"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.before_first_request
    def create_db():
        db.create_all()

    app.register_blueprint(factory_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(workstation_bp)
    app.register_blueprint(face_bp)
    app.register_blueprint(model_bp)

    return app

