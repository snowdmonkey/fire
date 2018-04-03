from flask import Blueprint, jsonify, request, abort
from .models import Workstation, worker_location
from ..factory.models import Factory
from ..worker.models import Worker
from ..database import db
import json

workstation_bp = Blueprint("workstation", __name__)


@workstation_bp.route("/factory/<int:factory_id>/workstation", methods=["GET"])
def get_workstation_list(factory_id: int):
    name_contain = request.args.get("nameContain")
    q = Workstation.query.filter_by(factory_id=factory_id)
    if name_contain is not None:
        q = q.filter(Workstation.name.contains(name_contain))

    result = [workstation.dict for workstation in q.all()]
    return jsonify(result)


@workstation_bp.route("/factory/<int:factory_id>/workstation/<int:workstation_id>", methods=["GET"])
def get_workstation(factory_id: int, workstation_id: int):
    workstation = Workstation.query.filter_by(id=workstation_id, factory_id=factory_id).first()
    if workstation is None:
        abort(404, "fail to find the workstation in this factory")
    else:
        return jsonify(workstation.dict)


@workstation_bp.route("/factory/<int:factory_id>/workstation", methods=["POST"])
def add_workstation(factory_id: int):
    factory = Factory.query.filter_by(id=factory_id).first()
    if factory is None:
        abort(404, "no such factory id")

    request_body = request.get_json()
    workstation_name = request_body.get("name")
    workstation_id = request_body.get("workstationId")
    description = request_body.get("description")
    if workstation_name is None:
        abort(400, "need a name for workstation")
    workstation = Workstation(id=workstation_id, name=workstation_name, description=description)
    factory.workstations.append(workstation)
    # db.session.add(workstation)
    db.session.commit()
    return "OK"


@workstation_bp.route("/workstation/<int:workstation_id>/worker", methods=["GET"])
def get_workers_in_station(workstation_id: int):
    workstation = Workstation.query.get_or_404(workstation_id)
    workers = workstation.workers

    result = list()
    for worker in workers:
        d = {"eid": worker.eid,
             "name": worker.name}
        face = worker.faces[0]
        encoding = json.loads(face.encoding)
        d.update({"faceEncoding": encoding})
        result.append(d)

    return jsonify(result)


@workstation_bp.route("/factory/<int:factory_id>/workstation/<int:workstation_id>/worker", methods=["POST"])
def add_worker_to_station(factory_id: int, workstation_id: int):
    request_body = request.get_json()
    worker_eid = request_body.get("eid")

    if worker_eid is None:
        abort(400, "need to provide a worker id")
    else:
        worker = Worker.query.filter_by(eid=worker_eid, factory_id=factory_id).first_or_404()
        workstation = Workstation.query.filter_by(id=workstation_id).first_or_404()
        workstation.workers.append(worker)
        db.session.commit()

    return "OK"
