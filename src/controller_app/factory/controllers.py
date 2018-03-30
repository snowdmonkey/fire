from flask import Blueprint, jsonify, request, abort
from .models import *
from ..database import db

factory_bp = Blueprint("factory", __name__)


@factory_bp.route("/factory", methods=["GET"])
def get_factories():
    name_contain = request.args.get("nameContain")
    if name_contain is None:
        q = Factory.query
    else:
        q = Factory.query.filter(Factory.name.contains(name_contain))
    results = [factory.dict for factory in q.all()]
    return jsonify(results)


@factory_bp.route("/factory/<int:factory_id>", methods=["GET"])
def get_factory_by_id(factory_id: int):
    factory = Factory.query.filter_by(id=factory_id).first()
    if factory is None:
        abort(404, "no such factory id")
    else:
        return jsonify(factory.dict)


@factory_bp.route("/factory", methods=["POST"])
def add_factory():
    post_body = request.get_json()
    factory_id = post_body.get("factoryId")
    factory_name = post_body.get("name")
    factory_description = post_body.get("description")
    if factory_id is None:
        abort(400, "need to provide factory id")
    if factory_name is None:
        abort(400, "need to provide factory name")
    else:
        factory = Factory(id=factory_id, name=factory_name, description=factory_description)
        db.session.add(factory)
        db.session.commit()
    return "OK"

