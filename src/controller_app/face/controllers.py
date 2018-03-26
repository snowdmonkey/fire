from flask import Blueprint, jsonify, request, abort, send_file

from .models import Face
from ..database import db
from ..worker.models import Worker

import cv2
import face_recognition
import numpy as np
import json
import io

face_bp = Blueprint("face", __name__)


@face_bp.route("/factory/<int:factory_id>/worker/<string:eid>/face", methods=["GET"])
def get_faces_of_worker(factory_id: int, eid: str):
    worker = Worker.query.filter_by(eid=eid, factory_id=factory_id).fist_or_404()
    return jsonify([face.dict for face in worker.faces])


@face_bp.route("/face/<int:face_id>/img", methods=["GET"])
def get_face_image_by_id(face_id: int):
    face = Face.query.get_or_404(face_id)
    return send_file(io.BytesIO(face.img),
                     mimetype="image/jpeg",
                     as_attachment=True,
                     attachment_filename="{}.jpg".format(face.worker.name))


@face_bp.route("/factory/<int:factory_id>/worker/<string:eid>/face", methods=["POST"])
def add_face_to_worker(factory_id: int, eid: str):
    worker = Worker.query.filter_by(eid=eid, factory_id=factory_id).first_or_404()
    file = request.files.get("file")

    if file is None:
        abort(400, "did not find file")
    elif file.filename == "":
        abort(400, "need to upload a jpg image")
    elif not file.filename.lower().endswith(".jpg"):
        abort(400, "need to upload a jpg image")
    else:
        img_raw = file.read()
        nparr = np.fromstring(img_raw, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        try:
            encodings = face_recognition.face_encodings(img)
        except Exception as e:
            abort(400, "face encoding failed")
        else:
            if len(encodings) > 1:
                abort(400, "more than more faces detected")
            else:
                encoding = encodings[0]
                encoding_str = json.dumps(encoding.tolist())
                face = Face(img=img_raw, encoding=encoding_str)
                worker.faces.append(face)
                db.session.commit()
                return "OK"

