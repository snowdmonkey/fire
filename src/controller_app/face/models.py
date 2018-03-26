from ..database import db
import json


class Face(db.Model):
    __tablename__ = "faces"
    id = db.Column(db.Integer, primary_key=True)
    worker_eid = db.Column(db.String(20))
    factory_id = db.Column(db.Integer)
    encoding = db.Column(db.TEXT)
    img = db.Column(db.LargeBinary)

    @property
    def dict(self):
        return {
            "id": self.id,
            "eid": self.worker_eid,
            "factoryId": self.factory_id,
            "encoding": json.loads(self.encoding)
        }

    __table_args__ = (
        db.ForeignKeyConstraint(
            ("factory_id", "worker_eid"),
            ("workers.factory_id", "workers.eid")
        ),
    )



# class FaceEncoding(db.Model):
#     __tablename__ = "face_encodings"
#     id = db.Column(db.Integer, primary_key=True)
#     order = db.Column(db.Integer)
#     encoding = db.Column(db.Float)
#     face_id = db.Column(db.Integer, db.ForeignKey("faces.id"), index=True)