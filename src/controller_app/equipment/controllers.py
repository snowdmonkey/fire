from flask import Blueprint, jsonify, request, abort
from ..database import db
from ..factory.models import Factory
from ..workstation.models import Workstation
from .models import Equipment
import logging

equipment_bp = Blueprint("equipment", __name__)

logger = logging.getLogger(__name__)


@equipment_bp.route("/factory/<int:factory_id>/equipment", methods=["POST"])
def add_equipment(factory_id: int):
    factory = Factory.query.get_or_404(factory_id)
    request_body = request.get_json()
    equipment_id = request_body.get("equipmentId")
    description = request_body.get("description")
    if equipment_id is None:
        abort(400, "need to provide equipment id")

    equipment = Equipment.query.get(equipment_id)
    if equipment is not None:
        abort(400, "equipment id duplicate")
    equipment = Equipment(id=int(equipment_id), description=description)
    try:
        factory.equipments.append(equipment)
        db.session.commit()
    except Exception as e:
        logger.exception(e)
        abort(500, "write to database failed")
    else:
        return "OK"


@equipment_bp.route("/factory/<int:factory_id>/workstation/<int:workstation_id>/equipment", methods=["POST"])
def add_equipment_to_workstation(factory_id: int, workstation_id: int):
    request_body = request.get_json()
    equipment_id = request_body.get("equipmentId")
    if equipment_id is None:
        abort(400, "need to provide equipment id")
    else:
        equipment_id = int(equipment_id)

    factory = Factory.query.get_or_404(factory_id)
    workstation = Workstation.query.get_or_404(workstation_id)
    if workstation.factory_id != factory_id:
        abort(400, "workstation does not belong to this factory")

    equipment = Equipment.query.get(equipment_id)

    if equipment is None:
        equipment = Equipment(id=equipment_id)
        try:
            factory.equipments.append(equipment)
            workstation.equipments.append(equipment)
            db.session.rollback()
        except Exception as e:
            logger.exception(e)
            db.session.rollback()
            abort(500, "fail to write to database")
        else:
            return "OK"
    else:
        if equipment.factory_id != factory_id:
            abort(400, "this equipment does not belong to this factory")
        else:
            try:
                workstation.equipments.append(equipment)
                db.session.commit()
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                abort(500, "fail to write to database")
            else:
                return "OK"

