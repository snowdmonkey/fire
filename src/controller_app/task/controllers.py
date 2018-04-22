import json
import logging
from datetime import datetime

# from dateutil.tz import tzlocal
from flask import Blueprint, jsonify, abort, current_app, request
# import paho.mqtt.client as mqtt
from kafka import KafkaProducer

from .models import Task, TaskType, TaskStatus
from ..database import db
from ..factory.models import Factory
from ..workstation.models import Workstation
from ..equipment.models import Equipment

task_bp = Blueprint("task", __name__)

logger = logging.getLogger(__name__)
# logger = current_app.logger


@task_bp.route("/task/equipment/equipment/<int:equipment_id>", methods=["POST"])
def add_equipment_task(equipment_id: int):
    body = request.get_json()
    deadline = body.get("deadline")
    try:
        deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
    except (TypeError, ValueError) as e:
        logger.error(e)
        abort(400, "deadline not provided or not in %Y-%m-%dT%H:%M:%S format")

    equipment = Equipment.query.get_or_404(equipment_id)

    if equipment.equipment_camera is None:
        abort(400, "no camera is registered for this equipment for checking existence")
    payload = {"equipmentId": equipment_id, "deadline": deadline.strftime(format="%Y-%m-%dT%H:%M:%S")}
    # payload = json.dumps(payload)

    task = Task(type=TaskType.equipment,
                create_time=datetime.now(),
                context=json.dumps(payload),
                deadline=deadline,
                status=TaskStatus.created)

    try:
        db.session.add(task)
        db.session.flush()
    except Exception as e:
        logger.exception(e)
        abort(500, "database write error")

    payload.update({"taskId": task.id})
    payload = json.dumps(payload)

    try:
        producer = KafkaProducer(bootstrap_servers=current_app.config.get("KAFKA_SERVER"))
        producer.send(topic="equipment", value=payload.encode())
        producer.close()
    except Exception as e:
        logger.error(e, exc_info=True)
        db.session.rollback()
        abort(500, "mq publish failed")
    else:
        db.session.commit()
        return jsonify(task.dict)


@task_bp.route("/task/equipment_active/equipment/<int:equipment_id>", methods=["POST"])
def add_equipment_active_task(equipment_id: int):
    body = request.get_json()
    deadline = body.get("deadline")
    try:
        deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
    except (TypeError, ValueError) as e:
        logger.error(e)
        abort(400, "deadline not provided or not in %Y-%m-%dT%H:%M:%S format")

    equipment = Equipment.query.get_or_404(equipment_id)

    if equipment.equipment_active_camera is None:
        abort(400, "no camera is registered for this equipment for checking existence")
    payload = {"equipmentId": equipment_id,
               "deadline": deadline.strftime(format="%Y-%m-%dT%H:%M:%S")}

    task = Task(type=TaskType.equipment_active,
                create_time=datetime.now(),
                context=json.dumps(payload),
                deadline=deadline,
                status=TaskStatus.created)

    try:
        db.session.add(task)
        db.session.flush()
    except Exception as e:
        logger.exception(e)
        abort(500, "database write error")

    payload.update({"taskId": task.id})
    payload = json.dumps(payload)

    try:
        producer = KafkaProducer(bootstrap_servers=current_app.config.get("KAFKA_SERVER"))
        producer.send(topic="equipment_active", value=payload.encode())
        producer.close()
    except Exception as e:
        logger.error(e, exc_info=True)
        db.session.rollback()
        abort(500, "mq publish failed")
    else:
        db.session.commit()
        return jsonify(task.dict)


@task_bp.route("/task/keyperson/workstation/<int:workstation_id>", methods=["POST"])
def add_keyperson_task(workstation_id: int):
    body = request.get_json()
    deadline = body.get("deadline")
    duration = body.get("duration")

    try:
        deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
    except (TypeError, ValueError) as e:
        logger.error(e)
        abort(400, "deadline not provided or not in %Y-%m-%dT%H:%M:%S format")

    if not isinstance(duration, int):
        abort(400, "task duration not provided or is not integer")

    workstation = Workstation.query.get_or_404(workstation_id)

    if workstation.camera is None:
        abort(400, "no camera is registered for this workstation for checking existence")

    payload = {
        "workstationId": workstation_id,
        "deadline": deadline.strftime(format="%Y-%m-%dT%H:%M:%S"),
        "duration": duration
    }

    task = Task(type=TaskType.keyperson,
                create_time=datetime.now(),
                context=json.dumps(payload),
                deadline=deadline,
                status=TaskStatus.created)

    try:
        db.session.add(task)
        db.session.flush()
    except Exception as e:
        logger.exception(e)
        abort(500, "database write error")

    payload.update({"taskId": task.id})
    payload = json.dumps(payload)

    try:
        producer = KafkaProducer(bootstrap_servers=current_app.config.get("KAFKA_SERVER"))
        producer.send(topic="keyperson", value=payload.encode())
        producer.close()
    except Exception as e:
        logger.error(e, exc_info=True)
        db.session.rollback()
        abort(500, "mq publish failed")
    else:
        db.session.commit()
        return jsonify(task.dict)


@task_bp.route("/task/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.dict)


@task_bp.route("/task/<int:task_id>", methods=["PUT"])
def set_task(task_id: int):
    body = request.get_json()

    task = Task.query.get_or_404(task_id)

    if "startTime" in body:
        task.start_time = datetime.strptime(body.get("startTime"), "%Y-%m-%dT%H:%M:%S")

    if "endTime" in body:
        task.end_time = datetime.strptime(body.get("endTime"), "%Y-%m-%dT%H:%M:%S")

    if "status" in body:
        task.status = body.get("status")

    if "result" in body:
        task.result = body.get("result")

    db.session.commit()
    return "OK"
