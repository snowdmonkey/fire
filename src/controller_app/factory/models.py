from ..database import db
import enum


class TaskType(enum.Enum):
    face = 1
    equipment = 2
    equipment_move = 3


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(TaskType))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    length = db.Column(db.Integer)  # the length of the video should be analyzed, in seconds


class Factory(db.Model):
    __tablename__ = "factories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(200))
    workers = db.relationship("Worker", backref="factory", lazy=True)
    workstations = db.relationship("WorkStation", backref="factory", lazy=True)
    equipment_model = db.relationship("EquipmentModel", backref="factory", uselist=False, lazy=True)
    equipment_cameras = db.relationship("EquipmentCamera", backref="factory", lazy=True)
    equipment_active_cameras = db.relationship("EquipmentActiveCamera", backref="factory", lazy=True)

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
