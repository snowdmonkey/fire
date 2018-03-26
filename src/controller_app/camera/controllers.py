from flask import Blueprint, jsonify, request, abort

from .models import EquipmentActiveCamera, EquipmentCamera, WorkstationCamera
from ..database import db
from ..factory.models import Factory
from ..workstation.models import WorkStation

camera_bp = Blueprint("camera", __name__)


@camera_bp.route("/factory/<int:factory_id>/equipment_camera", methods=["GET"])
def get_equipment_camera_by_factory(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)
    result = [camera.dict for camera in factory.equipment_cameras]
    return jsonify(result)


@camera_bp.route("/factory/<int:factory_id>/equipment_camera", methods=["POST"])
def add_equipment_camera(factory_id: int):
    request_json = request.get_json()
    if not {"uri", "xmin", "xmax", "ymin", "ymax"}.issubset(request_json):
        abort(400, "need to provide uri, xmin, xmax, ymin, ymax in json body")

    camera = EquipmentCamera(uri=request_json.get("uri"),
                             xmin=request_json.get("xmin"),
                             xmax=request_json.get("xmax"),
                             ymin=request_json.get("ymin"),
                             ymax=request_json.get("ymax"))
    factory = Factory.query.get_or_404(factory_id)
    factory.equipment_cameras.append(camera)
    db.session.commit()
    return "OK"


@camera_bp.route("/factory/<int:factory_id>/equipment_active_camera", methods=["GET"])
def get_equipment_active_camera_by_factory(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)
    result = [camera.dict for camera in factory.equipment_active_cameras]
    return jsonify(result)


@camera_bp.route("/factory/<int:factory_id>/equipment_active_camera", methods=["POST"])
def add_equipment_active_camera(factory_id: int):
    request_json = request.get_json()
    if not {"uri", "xmin", "xmax", "ymin", "ymax"}.issubset(request_json):
        abort(400, "need to provide uri, xmin, xmax, ymin, ymax in json body")

    camera = EquipmentActiveCamera(uri=request_json.get("uri"),
                                   xmin=request_json.get("xmin"),
                                   xmax=request_json.get("xmax"),
                                   ymin=request_json.get("ymin"),
                                   ymax=request_json.get("ymax"))
    factory = Factory.query.get_or_404(factory_id)
    factory.equipment_active_cameras.append(camera)
    db.session.commit()
    return "OK"


@camera_bp.route("/workstation/<int:workstation_id>/camera", methods=["GET"])
def get_camera_of_station(workstation_id: int):
    workstation = WorkStation.query.get_or_404(workstation_id)
    camera = workstation.camera
    if camera is None:
        abort(404, "No camera information for this workstation")
    return jsonify(camera.dict)


@camera_bp.route("/workstation/<int:workstation_id>/camera", methods=["PUT"])
def set_camera_of_station(workstation_id: int):
    request_json = request.get_json()
    if "uri" not in request_json:
        abort(400, "need to provide camera uri")

    camera = WorkstationCamera(uri=request_json.get("uri"))
    workstation = WorkStation.query.get_or_404(workstation_id)
    workstation.camera = camera
    db.session.commit()
    return "OK"
