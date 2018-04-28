from flask import Blueprint, request, abort, jsonify

from .models import Camera, EquipmentCameraAssociation, EquipmentActiveCameraAssociation
from ..database import db
from ..equipment.models import Equipment
from ..workstation.models import Workstation

camera_bp = Blueprint("camera", __name__)


@camera_bp.route("/camera", methods=["POST"])
def add_camera():
    request_json = request.get_json()
    if request_json is None:
        abort(400, "cannot retrieve json body")

    if not {"uri", "cameraId"}.issubset(request_json):
        abort(400, "need to provide camera uri in json body")

    uri = request_json.get("uri")
    camera_id = request_json.get("cameraId")

    if Camera.query.get(camera_id) is not None:
        abort(400, "camera id already exists")

    camera = Camera(id=camera_id, uri=uri)
    db.session.add(camera)
    db.session.commit()
    return "OK", 201


@camera_bp.route("/camera/<string:camera_id>", methods=["PUT"])
def set_camera(camera_id: str):
    request_json = request.get_json()
    if request_json is None:
        abort(400, "cannot retrieve json body")

    camera = Camera.query.get(camera_id)
    if camera is None:
        abort(404, "unknown camera id")

    if "uri" in request_json:
        camera.uri = request_json.get("uri")

    db.session.commit()
    return "OK"


@camera_bp.route("/camera/equipment_camera/equipment/<int:equipment_id>", methods=["PUT"])
def set_equipment_camera(equipment_id: int):
    request_json = request.get_json()
    if not {"xmin", "xmax", "ymin", "ymax", "cameraId"}.issubset(request_json):
        abort(400, "need to provide xmin, xmax, ymin, ymax, cameraId in json body")

    try:
        xmin = float(request_json.get("xmin"))
        xmax = float(request_json.get("xmax"))
        ymin = float(request_json.get("ymin"))
        ymax = float(request_json.get("ymax"))
    except (ValueError, TypeError):
        abort(400, "need to provide xmin, xmax, ymin, ymax as float")

    if not 0.0 <= xmin < xmax <= 1.0:
        abort(400, "0.0 <= xmin < xmax <= 1.0 not satisfied")

    if not 0.0 <= ymin < ymax <= 1.0:
        abort(400, "0.0 <= ymin < ymax <= 1.0 not satisfied")

    camera_id = request_json.get("cameraId")
    camera = Camera.query.get(camera_id)
    if camera is None:
        abort(400, "no such camera id")

    equipment = Equipment.query.get_or_404(equipment_id)

    association = EquipmentCameraAssociation.query.filter_by(equipment_id=equipment_id).first()

    if association is None:

        association = EquipmentCameraAssociation(xmin=xmin,
                                                 xmax=xmax,
                                                 ymin=ymin,
                                                 ymax=ymax)
        with db.session.no_autoflush:
            association.camera = camera
            association.equipment = equipment

        db.session.flush()
        db.session.commit()

    else:
        association.xmin = xmin
        association.xmax = xmax
        association.ymin = ymin
        association.ymax = ymax
        association.camera = camera
        db.session.commit()

    return "OK"


@camera_bp.route("/camera/equipment_active_camera/equipment/<int:equipment_id>", methods=["PUT"])
def set_equipment_active_camera(equipment_id: int):
    request_json = request.get_json()
    if not {"xmin", "xmax", "ymin", "ymax", "cameraId"}.issubset(request_json):
        abort(400, "need to provide xmin, xmax, ymin, ymax, cameraId in json body")

    try:
        xmin = float(request_json.get("xmin"))
        xmax = float(request_json.get("xmax"))
        ymin = float(request_json.get("ymin"))
        ymax = float(request_json.get("ymax"))
    except (ValueError, TypeError):
        abort(400, "need to provide xmin, xmax, ymin, ymax as float")

    if not 0.0 <= xmin < xmax <= 1.0:
        abort(400, "0.0 <= xmin < xmax <= 1.0 not satisfied")

    if not 0.0 <= ymin < ymax <= 1.0:
        abort(400, "0.0 <= ymin < ymax <= 1.0 not satisfied")

    camera_id = request_json.get("cameraId")
    camera = Camera.query.get(camera_id)
    if camera is None:
        abort(400, "no such camera id")

    equipment = Equipment.query.get_or_404(equipment_id)

    association = EquipmentActiveCameraAssociation.query.filter_by(equipment_id=equipment_id).first()

    if association is None:

        association = EquipmentActiveCameraAssociation(xmin=xmin,
                                                       xmax=xmax,
                                                       ymin=ymin,
                                                       ymax=ymax)
        with db.session.no_autoflush:
            association.camera = camera
            association.equipment = equipment

        db.session.flush()
        db.session.commit()

    else:
        association.xmin = xmin
        association.xmax = xmax
        association.ymin = ymin
        association.ymax = ymax
        association.camera = camera
        db.session.commit()

    return "OK"


@camera_bp.route("/camera/keyperson_camera/workstation/<int:workstation_id>", methods=["PUT"])
def set_keyperson_camera(workstation_id: int):
    request_json = request.get_json()
    if not {"cameraId"}.issubset(request_json):
        abort(400, "need to provide cameraId in json body")

    workstation = Workstation.query.get_or_404(workstation_id)
    camera_id = request_json.get("cameraId")
    camera = Camera.query.get(camera_id)
    if camera is None:
        abort(400, "camera id not found")

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
