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
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(60))
    admin = db.Column(db.Boolean)
    charging_sessions = db.relationship('ChargingSession')

class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(150))    