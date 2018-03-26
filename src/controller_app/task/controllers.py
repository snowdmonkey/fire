from flask import Blueprint, jsonify, request, abort, current_app
from ..database import db
from ..factory.models import Factory
from ..workstation.models import WorkStation
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import logging

task_bp = Blueprint("task", __name__)

logger = logging.getLogger(__name__)


@task_bp.route("/task/equipment/factory/<int:factory_id>", methods=["POST"])
def add_equipment_task(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)
    client = mqtt.Client(client_id="client-0001")
    client.username_pw_set(username=current_app.config.get("MQTT_USER"),
                           password=current_app.config.get("MQTT_PWD"))
    client.connect(host=current_app.config.get("MQTT_HOST"),
                   port=current_app.config.get("MQTT_PORT"))

    payload = {"factoryId": factory_id,
               "datetime": datetime.now().strftime(format="%Y-%m-%dT%H:%M:%S")}
    try:
        push = client.publish(topic="task/equipment", payload=json.dumps(payload))
    except Exception as e:
        logger.error(e, exc_info=True)
        abort(500, "mqtt publish failed")
    else:
        if push.is_published() is not True:
            abort(500, "mqtt publish failed")
    finally:
        client.disconnect()

    return "OK"


@task_bp.route("/task/keyperson/workstation/<int:workstation_id>", methods=["POST"])
def add_keyperson_task(workstation_id: int):
    workstation = WorkStation.query.get_or_404(workstation_id)
    client = mqtt.Client(client_id="client-0001")
    client.username_pw_set(username=current_app.config.get("MQTT_USER"),
                           password=current_app.config.get("MQTT_PWD"))
    client.connect(host=current_app.config.get("MQTT_HOST"),
                   port=current_app.config.get("MQTT_PORT"))

    payload = {"workstationId": workstation_id,
               "datetime": datetime.now().strftime(format="%Y-%m-%dT%H:%M:%S")}
    try:
        push = client.publish(topic="task/keyperson", payload=json.dumps(payload))
    except Exception as e:
        logger.error(e, exc_info=True)
        abort(500, "mqtt publish failed")
    else:
        if push.is_published() is not True:
            abort(500, "mqtt publish failed")
    finally:
        client.disconnect()

    return "OK"
