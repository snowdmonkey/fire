import json
import logging
from datetime import datetime

from dateutil.tz import tzlocal
from flask import Blueprint, jsonify, abort, current_app
# import paho.mqtt.client as mqtt
from kafka import KafkaProducer

from .models import Task, TaskType, TaskStatus
from ..database import db
from ..factory.models import Factory
from ..workstation.models import WorkStation

task_bp = Blueprint("task", __name__)

logger = logging.getLogger(__name__)


@task_bp.route("task/equipment/<int:equipment_id>", methods=["GET"])
def add_equipment_task(equipment_id: int):
    equipment =


@task_bp.route("/task/equipment/factory/<int:factory_id>", methods=["POST"])
def add_equipment_task(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)
    # client = mqtt.Client(client_id="")
    # client.username_pw_set(username=current_app.config.get("MQTT_USER"),
    #                        password=current_app.config.get("MQTT_PWD"))
    # client.connect(host=current_app.config.get("MQTT_HOST"),
    #                port=current_app.config.get("MQTT_PORT"))

    payload = {"factoryId": factory_id,
               "datetime": datetime.now(tz=tzlocal()).strftime(format="%Y-%m-%dT%H:%M:%S%z")}
    payload = json.dumps(payload)
    try:
        # push = client.publish(topic="task/equipment", payload=payload)
        # push_code, _= mqtt.publish(topic="task/equipment", payload=payload)
        producer = KafkaProducer(bootstrap_servers=current_app.config.get("KAFKA_SERVER"))
        producer.send(topic="equipment", value=payload.encode())
        producer.close()
    except Exception as e:
        logger.error(e, exc_info=True)
        abort(500, "mq publish failed")
    # finally:
    #     client.disconnect()

    # if push_code != 0:
    #     abort(500, "mqtt publish failed")
    # else:
    #     task = Task(type=TaskType.equipment,
    #                 create_time=datetime.now(tz=tzlocal()),
    #                 context=payload,
    #                 status=TaskStatus.created)
    #     db.session.add(task)
    #     db.session.commit()
    #     return jsonify(task.dict)
    task = Task(type=TaskType.equipment,
                create_time=datetime.now(tz=tzlocal()),
                context=payload,
                status=TaskStatus.created)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.dict)


@task_bp.route("/task/keyperson/workstation/<int:workstation_id>", methods=["POST"])
def add_keyperson_task(workstation_id: int):
    workstation = WorkStation.query.get_or_404(workstation_id)
    # client = mqtt.Client(client_id="")
    # client.username_pw_set(username=current_app.config.get("MQTT_USER"),
    #                        password=current_app.config.get("MQTT_PWD"))
    # client.connect(host=current_app.config.get("MQTT_HOST"),
    #                port=current_app.config.get("MQTT_PORT"))

    payload = {"workstationId": workstation_id,
               "datetime": datetime.now(tz=tzlocal()).strftime(format="%Y-%m-%dT%H:%M:%S%z")}
    payload = json.dumps(payload)
    try:
        # push_code, _ = mqtt.publish(topic="task/keyperson", payload=payload)
        # push = client.publish(topic="task/keyperson", payload=payload)
        producer = KafkaProducer(bootstrap_servers=current_app.config.get("KAFKA_SERVER"))
        producer.send(topic="keyperson", value=payload.encode())
        producer.close()
    except Exception as e:
        logger.error(e, exc_info=True)
        abort(500, "mqtt publish failed")
    # finally:
    #     client.disconnect()

    # if push_code != 0:
    #     abort(500, "mqtt publish failed")
    # else:
    #     task = Task(type=TaskType.face,
    #                 create_time=datetime.now(tz=tzlocal()),
    #                 context=payload,
    #                 status=TaskStatus.created)
    #     db.session.add(task)
    #     db.session.commit()
    #     return jsonify(task.dict)
    task = Task(type=TaskType.face,
                create_time=datetime.now(tz=tzlocal()),
                context=payload,
                status=TaskStatus.created)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.dict)


@task_bp.route("/task/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.dict)