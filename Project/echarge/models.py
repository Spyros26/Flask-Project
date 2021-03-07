from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    connection_date = db.Column(db.String(60))
    connection_time = db.Column(db.String(60))
    disconnection_date = db.Column(db.String(60))
    disconnection_time = db.Column(db.String(60))
    kWh_delivered = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    point_id = db.Column(db.Integer, db.ForeignKey('point.id'))
    


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(60))
    is_admin = db.Column(db.Boolean)
    charging_sessions = db.relationship('Session')
    evs = db.relationship('EVehicle')

class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(150))

class EVehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.String(100), unique=True)
    brand = db.Column(db.String(20))
    car_type = db.Column(db.String(10))
    brand_id = db.Column(db.String(100))
    model = db.Column(db.String(40))
    release_year = db.Column(db.Integer)
    variant = db.Column(db.String(20))
    usable_battery_size = db.Column(db.Float)
    ac_charger = db.Column(JSON)
    dc_charger = db.Column(JSON)
    energy_consumption = db.Column(JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(100))
    website = db.Column(db.String(150))
    email = db.Column(db.String(150))
    
class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(50), unique=True)
    address = db.Column(db.String(120))
    latitude = db.Column(db.String(25))
    longitude = db.Column(db.String(25))
    points = db.relationship('Point')

class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.String(50), unique=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    sessions = db.relationship('Session')

class EnergyProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)


