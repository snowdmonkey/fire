from ..database import db
from sqlalchemy.dialects.mysql import LONGBLOB
import json


class EquipmentModel(db.Model):
    __tablename__ = "equipment_models"
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.id"))
    # class_map = db.Column(db.TEXT)
    pb = db.Column(LONGBLOB)
    md5 = db.Column(db.String(50))

    @property
    def dict(self):
        return {
            "id": self.id,
            "equipmentId": self.equipment_id,
            # "mapping": json.loads(self.class_map),
            "md5": self.md5
        }