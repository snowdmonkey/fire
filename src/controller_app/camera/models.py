from ..database import db


class EquipmentCamera(db.Model):
    __tablename__ = "equipment_cameras"
    id = db.Column(db.String(60), primary_key=True)
    uri = db.Column(db.String(100), unique=True)
    xmin = db.Column(db.Float)
    xmax = db.Column(db.Float)
    ymin = db.Column(db.Float)
    ymax = db.Column(db.Float)
    # factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"))
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.id"))

    @property
    def dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "xmin": self.xmin,
            "xmax": self.xmax,
            "ymin": self.ymin,
            "ymax": self.ymax,
            "equipmentId": self.factory_id
        }


class EquipmentActiveCamera(db.Model):
    __tablename__ = "equipment_active_cameras"
    id = db.Column(db.String(60), primary_key=True)
    uri = db.Column(db.String(100), unique=True)
    xmin = db.Column(db.Float)
    xmax = db.Column(db.Float)
    ymin = db.Column(db.Float)
    ymax = db.Column(db.Float)
    # factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"))
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.id"))

    @property
    def dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "xmin": self.xmin,
            "xmax": self.xmax,
            "ymin": self.ymin,
            "ymax": self.ymax,
            "equipmentId": self.factory_id
        }


class WorkstationCamera(db.Model):
    __tablename__ = "workstation_camera"
    id = db.Column(db.String(60), primary_key=True)
    uri = db.Column(db.String(100), unique=True)
    workstation_id = db.Column(db.Integer, db.ForeignKey("workstations.id"))

    @property
    def dict(self):
        return {
            "id": self.id,
            "uri": self.uri,
            "workstationId": self.workstation_id
        }