from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class ChargingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    EV = db.Column(db.String(10))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    charging_program = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    charging_sessions = db.relationship('ChargingSession')
