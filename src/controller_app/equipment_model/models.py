from ..database import db
import json


class EquipmentModel(db.Model):
    __tablename__ = "equipment_models"
    id = db.Column(db.Integer, primary_key=True)
    factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"))
    class_map = db.Column(db.TEXT)
    pb = db.Column(db.LargeBinary)
    md5 = db.Column(db.String(50))

    @property
    def dict(self):
        return {
            "mapping": json.loads(self.class_map),
            "md5": self.md5
        }