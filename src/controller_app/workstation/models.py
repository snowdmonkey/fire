from ..database import db


worker_location = db.Table(
    "worker_location",
    db.Column("workstation_id", db.Integer, db.ForeignKey("workstations.id"), primary_key=True),
    db.Column("worker_eid", db.String(20), primary_key=True),
    db.Column("factory_id", db.Integer, primary_key=True),
    db.ForeignKeyConstraint(
        ("factory_id", "worker_eid"),
        ("workers.factory_id", "workers.eid")
    )
)


class Workstation(db.Model):
    __tablename__ = "workstations"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(50))
    description = db.Column(db.TEXT)
    factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"), index=True)
    workers = db.relationship(
        "Worker",
        secondary=worker_location,
        lazy="subquery",
        backref=db.backref("workers", lazy=True))
    camera = db.relationship("WorkstationCamera", backref="workstation", uselist=False, lazy=True)
    equipments = db.relationship("Equipment", backref="workstation", lazy=True)

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "factoryId": self.factory_id,
            "description": self.description,
            "workers": [worker.dict for worker in self.workers]
        }


