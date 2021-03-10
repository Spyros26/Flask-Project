from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(60))
    #is_admin = db.Column(db.Boolean)
    role = db.Column(db.String(20))
    #charging_sessions = db.relationship('Session')
    evs = db.relationship('Evehicle')

class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(150))

class Evehicle(db.Model):
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
    sessions = db.relationship('Session')

class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(100))
    website = db.Column(db.String(150))
    email = db.Column(db.String(150))
    stations = db.relationship('Station')
    
class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(50), unique=True)
    address = db.Column(db.String(120))
    latitude = db.Column(db.String(25))
    longitude = db.Column(db.String(25))
    points = db.relationship('Point')
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('energyprovider.id'))

class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    point_id = db.Column(db.String(50), unique=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    sessions = db.relationship('Session')

class Energyprovider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100), unique=True)
    stations = db.relationship('Station')


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    connection_date = db.Column(db.String(60))
    connection_time = db.Column(db.String(60))
    done_date = db.Column(db.String(60))
    done_time = db.Column(db.String(60))
    disconnection_date = db.Column(db.String(60))
    disconnection_time = db.Column(db.String(60))
    kWh_delivered = db.Column(db.Float)
    protocol = db.Column(db.String(40))
    payment = db.Column(db.String(40))
    point_id = db.Column(db.Integer, db.ForeignKey('point.id'))
    ev_id = db.Column(db.Integer, db.ForeignKey('evehicle.id'))
    

