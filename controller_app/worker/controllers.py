from flask import Blueprint, jsonify, request, abort
from .models import Worker
from ..factory.models import Factory
from ..database import db

worker_bp = Blueprint("worker", __name__)


@worker_bp.route("/factory/<int:factory_id>/worker/<string:worker_eid>", methods=["GET"])
def get_worker(factory_id: int, worker_eid: str):
    worker = Worker.query.filter_by(eid=worker_eid, factory_id=factory_id).first_or_404()
    return jsonify(worker.dict)


@worker_bp.route("/factory/<int:factory_id>/worker", methods=["GET"])
def get_worker_by_name(factory_id: int):
    worker_name = request.args.get("name")
    if worker_name is None:
        abort(400, "need to provide a name")
    workers = Worker.query.filter_by(factory_id=factory_id, name=worker_name).all()
    return jsonify([worker.dict for worker in workers])


@worker_bp.route("/factory/<int:factory_id>/worker", methods=["POST"])
def add_worker_to_factory(factory_id: int):
    factory = Factory.query.filter_by(id=factory_id).first_or_404()
    request_body = request.get_json()
    name = request_body.get("name")
    eid = request_body.get("eid")
    if name is None:
        abort(400, "need worker name")
    elif eid is None:
        abort(400, "need worker EID")
    else:
        worker = Worker(eid=eid, name=name)
        factory.workers.append(worker)
        db.session.commit()
        return "OK"
