from ..database import db


class Worker(db.Model):
    __tablename__ = "workers"
    eid = db.Column(db.String(20))
    factory_id = db.Column(db.Integer, db.ForeignKey("factories.id"), index=True)
    name = db.Column(db.String(20))
    faces = db.relationship("Face", backref="worker", lazy=True)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            "factory_id", "eid"
        ),
    )

    @property
    def dict(self):
        return {
            "eid": self.eid,
            "name": self.name
        }
