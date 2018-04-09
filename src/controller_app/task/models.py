import enum
from datetime import datetime
from ..database import db
from sqlalchemy.dialects.mysql import MEDIUMTEXT


class TaskType(enum.Enum):
    keyperson = 1
    equipment = 2
    equipment_active = 3


class TaskStatus(enum.Enum):
    created = 1
    ongoing = 2
    success = 3
    failed = 4


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(TaskType), index=True)
    deadline = db.Column(db.DATETIME)
    create_time = db.Column(db.DATETIME)
    start_time = db.Column(db.DATETIME)
    end_time = db.Column(db.DATETIME)
    context = db.Column(db.TEXT)
    status = db.Column(db.Enum(TaskStatus), index=True)
    result = db.Column(MEDIUMTEXT)

    @property
    def dict(self):
        result = {
            "id": self.id,
            "type": self.type.name,
            "createTime": datetime.strftime(self.create_time, "%Y-%m-%dT%H:%M:%S"),
            "deadline": datetime.strftime(self.deadline, "%Y-%m-%dT%H:%M:%S"),
            "context": self.context,
            "status": self.status.name,
            "result": self.result}
        if self.start_time is not None:
            result.update({"startTime": datetime.strftime(self.start_time, "%Y-%m-%dT%H:%M:%S")})
        if self.end_time is not None:
            result.update({"endTime": datetime.strftime(self.end_time, "%Y-%m-%dT%H:%M:%S")})
        return result


# class KeypersonTaskPayload:
#
#     def __init__(self, workstation_id: int, camera_id: str, deadline: datetime):
