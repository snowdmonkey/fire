from flask import Blueprint, jsonify, request, abort, send_file

from .models import EquipmentModel
from ..factory.models import Factory
from ..database import db

import io
import hashlib

model_bp = Blueprint("equipment_model", __name__)


@model_bp.route("/factory/<int:factory_id>/equipment_model/pb", methods=["GET"])
def get_model_pb(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)
    model = factory.equipment_model
    if model is None:
        abort(404, "model is not set")
    return send_file(io.BytesIO(model.pb),
                     mimetype="application/octet-stream",
                     as_attachment=True,
                     attachment_filename="factory-{}.pb".format(factory_id))


@model_bp.route("/factory/<int:factory_id>/equipment_model", methods=["GET"])
def get_model_mapping(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)
    model = factory.equipment_model
    if model is None:
        abort(404, "model is not set")
    return jsonify(model.dict)


@model_bp.route("/factory/<int:factory_id>/equipment_model", methods=["PUT"])
def set_equipment_mode(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)

    pb_file = request.files.get("file")
    # print(request.files)
    if pb_file is None:
        abort(400, "need a pb file")

    request_form = request.form
    mapping = request_form.get("mapping")
    if mapping is None:
        abort(400, "need to provide class mapping in json body")

    hasher = hashlib.md5()
    pb_binary = pb_file.read()
    hasher.update(pb_binary)
    md5_str = hasher.hexdigest()

    model = EquipmentModel(class_map=mapping, pb=pb_binary, md5=md5_str)
    factory.equipment_model = model

    db.session.commit()

    return "OK"
