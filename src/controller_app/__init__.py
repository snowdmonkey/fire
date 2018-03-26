"""app to control the setting of algorithm module of 3CF project
"""
from flask import Flask
from .database import db
from .factory import factory_bp
from .workstation import workstation_bp
from .worker import worker_bp
from .face import face_bp
from .equipment_model import model_bp
from .task import task_bp
from .camera import camera_bp


def create_app(db_uri: str, mqtt_host: str, mqtt_user: str, mqtt_pwd: str, mqtt_port: int):
    """
    create flask application
    :param db_uri: database uri to use
    :param mqtt_host: hostname for mqtt
    :param mqtt_port: port number for mqtt
    :param mqtt_user: username for mqtt
    :param mqtt_pwd: password for mqtt
    :return: flask app
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "\xea\x1e\xc2\x94\xec\xd9\xbf \x0flsG\xf6\xb5 \xa2~\x8c\x82\x17*\xfc{V"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MQTT_HOST"] = mqtt_host
    app.config["MQTT_PORT"] = mqtt_port
    app.config["MQTT_USER"] = mqtt_user
    app.config["MQTT_PWD"] = mqtt_pwd

    db.init_app(app)

    @app.before_first_request
    def create_db():
        db.create_all()

    app.register_blueprint(factory_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(workstation_bp)
    app.register_blueprint(face_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(camera_bp)

    return app

