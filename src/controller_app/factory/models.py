from ..database import db


class Factory(db.Model):
    __tablename__ = "factories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(200))

    workers = db.relationship("Worker", backref="factory", lazy=True)
    workstations = db.relationship("Workstation", backref="factory", lazy=True)
    equipment_model = db.relationship("EquipmentModel", backref="factory", uselist=False, lazy=True)
    # equipment_cameras = db.relationship("EquipmentCamera", backref="factory", lazy=True)
    # equipment_active_cameras = db.relationship("EquipmentActiveCamera", backref="factory", lazy=True)
    equipments = db.relationship("Equipment", backref="factory", lazy=True)

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
