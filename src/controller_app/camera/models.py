from ..database import db


class Camera(db.Model):
    __tablename__ = "cameras"
    id = db.Column(db.String(60), primary_key=True)
    uri = db.Column(db.String(300), unique=True)

    equipments = db.relationship("EquipmentCameraAssociation", backref="camera")
    active_equipments = db.relationship("EquipmentActiveCameraAssociation", backref="camera")
    workstation = db.relationship("Workstation", backref="camera", uselist=False)

    @property
    def dict(self):
        return {
            "id": self.id,
            "uri": self.uri
        }


class EquipmentCameraAssociation(db.Model):
    __tablename__ = "equipment_cameras"
    camera_id = db.Column(db.String(60), db.ForeignKey("cameras.id"), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.id"), primary_key=True)
    xmin = db.Column(db.Float)
    xmax = db.Column(db.Float)
    ymin = db.Column(db.Float)
    ymax = db.Column(db.Float)

    # camera = db.relationship("Camera", backref="equipments")
    # equipment = db.relationship("Equipment", backref="equipment_camera")

    @property
    def dict(self):
        return {
            "xmin": self.xmin,
            "xmax": self.xmax,
            "ymin": self.ymin,
            "ymax": self.ymax,
            "cameraId": self.camera_id,
            "equipmentId": self.equipment_id
        }


class EquipmentActiveCameraAssociation(db.Model):
    __tablename__ = "equipment_active_cameras"
    camera_id = db.Column(db.String(60), db.ForeignKey("cameras.id"), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.id"), primary_key=True)
    xmin = db.Column(db.Float)
    xmax = db.Column(db.Float)
    ymin = db.Column(db.Float)
    ymax = db.Column(db.Float)

    # camera = db.relationship("Camera", backref="equipments_active")
    # equipment = db.relationship("Equipment", backref="equipment_actives_camera")

    @property
    def dict(self):
        return {
            "xmin": self.xmin,
            "xmax": self.xmax,
            "ymin": self.ymin,
            "ymax": self.ymax,
            "cameraId": self.camera_id,
            "equipmentId": self.equipment_id
        }

# class EquipmentCamera(db.Model):
#     __tablename__ = "equipment_cameras"
#     id = db.Column(db.String(60), primary_key=True)
#     uri = db.Column(db.String(300), unique=True)
#     xmin = db.Column(db.Float)
#     xmax = db.Column(db.Float)
#     ymin = db.Column(db.Float)
#     ymax = db.Column(db.Float)
#     # factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"))
#     equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.id"))
#
#     @property
#     def dict(self):
#         return {
#             "id": self.id,
#             "uri": self.uri,
#             "xmin": self.xmin,
#             "xmax": self.xmax,
#             "ymin": self.ymin,
#             "ymax": self.ymax,
#             "equipmentId": self.equipment_id
#         }
#
#
# class EquipmentActiveCamera(db.Model):
#     __tablename__ = "equipment_active_cameras"
#     id = db.Column(db.String(60), primary_key=True)
#     uri = db.Column(db.String(300), unique=True)
#     xmin = db.Column(db.Float)
#     xmax = db.Column(db.Float)
#     ymin = db.Column(db.Float)
#     ymax = db.Column(db.Float)
#     # factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"))
#     equipment_id = db.Column(db.Integer, db.ForeignKey("equipments.id"))
#
#     @property
#     def dict(self):
#         return {
#             "id": self.id,
#             "uri": self.uri,
#             "xmin": self.xmin,
#             "xmax": self.xmax,
#             "ymin": self.ymin,
#             "ymax": self.ymax,
#             "equipmentId": self.equipment_id
#         }


# class WorkstationCamera(db.Model):
#     __tablename__ = "workstation_cameras"
#     id = db.Column(db.String(60), primary_key=True)
#     uri = db.Column(db.String(300), unique=True)
#     workstation_id = db.Column(db.Integer, db.ForeignKey("workstations.id"))
#
#     @property
#     def dict(self):
#         return {
#             "id": self.id,
#             "uri": self.uri,
#             "workstationId": self.workstation_id
#         }