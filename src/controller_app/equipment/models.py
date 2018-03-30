from ..database import db


class Equipment(db.Model):
    __tablename__ = "equipments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    description = db.Column(db.TEXT)
    factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"), index=True)
    workstation_id = db.Column(db.Integer, db.ForeignKey("workstations.id"), index=True)

    equipment_camera = db.relationship("EquipmentCamera", backref="equipment", uselist=False, lazy=True)
    equipment_active_camera = db.relationship("EquipmentActiveCamera", backref="equipment", uselist=False, lazy=True)

    @property
    def dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "factoryId": self.factory_id,
            "workstationId": self.workstation_id
        }