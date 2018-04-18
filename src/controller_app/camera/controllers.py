from flask import Blueprint, request, abort, jsonify

from .models import EquipmentActiveCamera, EquipmentCamera, WorkstationCamera
from ..database import db
from ..equipment.models import Equipment
from ..workstation.models import Workstation

camera_bp = Blueprint("camera", __name__)


@camera_bp.route("/camera/equipment_camera/equipment/<int:equipment_id>", methods=["PUT"])
def set_equipment_camera(equipment_id: int):
    request_json = request.get_json()
    if not {"uri", "xmin", "xmax", "ymin", "ymax", "cameraId"}.issubset(request_json):
        abort(400, "need to provide uri, xmin, xmax, ymin, ymax, cameraId in json body")

    camera = EquipmentCamera(uri=request_json.get("uri"),
                             xmin=request_json.get("xmin"),
                             xmax=request_json.get("xmax"),
                             ymin=request_json.get("ymin"),
                             ymax=request_json.get("ymax"),
                             id=request_json.get("cameraId"))
    equipment = Equipment.query.get_or_404(equipment_id)
    equipment.equipment_camera = camera
    db.session.commit()
    return "OK"


@camera_bp.route("/camera/equipment_active_camera/equipment/<int:equipment_id>", methods=["PUT"])
def set_equipment_active_camera(equipment_id: int):
    request_json = request.get_json()
    if not {"uri", "xmin", "xmax", "ymin", "ymax", "cameraId"}.issubset(request_json):
        abort(400, "need to provide uri, xmin, xmax, ymin, ymax, cameraId in json body")

    camera = EquipmentActiveCamera(uri=request_json.get("uri"),
                                   xmin=request_json.get("xmin"),
                                   xmax=request_json.get("xmax"),
                                   ymin=request_json.get("ymin"),
                                   ymax=request_json.get("ymax"),
                                   id=request_json.get("cameraId"))
    equipment = Equipment.query.get_or_404(equipment_id)
    equipment.equipment_active_camera = camera
    db.session.commit()
    return "OK"


@camera_bp.route("/camera/keyperson_camera/workstation/<int:workstation_id>", methods=["PUT"])
def set_keyperson_camera(workstation_id: int):
    request_json = request.get_json()
    if not {"uri", "cameraId"}.issubset(request_json):
        abort(400, "need to provide cameraId uri, in json body")

    workstation  = Workstation.query.get_or_404(workstation_id)
    camera = WorkstationCamera(id=request_json.get("cameraId"), uri=request_json.get("uri"))
    workstation.camera = camera
    db.session.commit()
    return "OK"


@camera_bp.route("/camera/keyperson_camera/workstation/<int:workstation_id>", methods=["GET"])
def get_keyperson_camera(workstation_id: int):
    workstation = Workstation.query.get_or_404(workstation_id)
    camera = workstation.camera
    if camera is None:
        abort(404, "no keyperson camera for this workstation")
    else:
        return jsonify(camera.dict)


@camera_bp.route("/camera/equipment_camera/equipment/<int:equipment_id>", methods=["GET"])
def get_equipment_camera(equipment_id: int):
    equipment = Equipment.query.get_or_404(equipment_id)
    camera = equipment.equipment_camera
    if camera is None:
        abort(404, "no equipment camera set for this equipment")
    else:
        return jsonify(camera.dict)