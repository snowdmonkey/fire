from ..database import db


class Worker(db.Model):
    __tablename__ = "workers"
    eid = db.Column(db.String(20), primary_key=True)
    factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"), index=True, primary_key=True)
    name = db.Column(db.String(20))
    faces = db.relationship("Face", backref="worker", lazy=True)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            "factory_id", "worker_eid"
        ),
    )

    @property
    def dict(self):
        return {
            "eid": self.eid,
            "name": self.name
        }
