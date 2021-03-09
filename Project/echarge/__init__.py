from flask import Flask
from flask_migrate import Migrate

from flask import Flask, jsonify

from flask_sqlalchemy import SQLAlchemy
from os import path

import uuid
from werkzeug.security import generate_password_hash
import pandas as pd
import json
import numpy as np
import random

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "Data.db"


def create_app():
    App = Flask(__name__, template_folder='./frontend/templates')
    App.config['SECRET_KEY'] = 'hjshjhdjh'
    App.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    App.config['JSON_SORT_KEYS'] = False
    db.init_app(App)

    from echarge.backend import views, auth, admin, sessions

    App.register_blueprint(views, url_prefix='/')
    App.register_blueprint(admin, url_prefix='/')
    App.register_blueprint(auth, url_prefix='/')
    App.register_blueprint(sessions, url_prefix='/')

    from .models import User, RevokedToken, Evehicle, Point, Station, Operator, Session

    create_database(App)
    migrate.init_app(App, db)

    return App


def create_database(app):
    if not path.exists('echarge/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

def default_admin(username, password):

    from .models import User
    user = User.query.filter_by(username=username).first()
    if not user:
        hashed_password = generate_password_hash(password, method='sha256')
        admin = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password, role="Admin")
        db.session.add(admin)
        db.session.commit()
        print('Default admin created!')
    else:
        user.password = generate_password_hash(password, method='sha256')
        db.session.add(user)
        db.session.commit()
        print('Default admin initialized')

def default_evs(filename):
    
    from .models import Evehicle, User

    with open(filename) as jsdata:
        evs = json.load(jsdata)

    cont = pd.DataFrame(evs['data'])    
    #cont = pd.read_json(filename)
    length = cont.shape[0]
    #print(cont)
    #print(length)
    for x in range(0,length):
        check = Evehicle.query.filter_by(car_id=cont["id"][x]).first()
        if not check:
            user = User.query.filter_by(username=f"User{x+1}").first()
            new_ev = Evehicle(car_id=cont["id"][x], brand=cont["brand"][x], 
                        car_type=cont["type"][x], brand_id=cont["brand_id"][x],
                        model=cont["model"][x], release_year=cont["release_year"][x],
                        variant=cont["variant"][x], usable_battery_size=cont["usable_battery_size"][x],
                        ac_charger=cont["ac_charger"][x], dc_charger=cont["dc_charger"][x],
                        energy_consumption=cont["energy_consumption"][x], user_id=user.id)
            db.session.add(new_ev)
            db.session.commit()
    print('Default EVs are in')                    

def default_operators(filename):

    from .models import Operator

    df = pd.read_csv(filename, sep=";")
    #print(df)
    length = df.shape[0]
    #print(length)

    for a, x in df.iterrows():
        check = Operator.query.filter_by(operator_id=x["ID"]).first()
        if not check:
            new_op = Operator(operator_id=x["ID"], name=x["Title"], 
                        website=x["WebsiteURL"], email=x["ContactEmail"])            
            db.session.add(new_op)
            db.session.commit()
    print('Default operators are in')        
    
def default_points_stations(filename):

    from .models import Station, Point, Operator
    
    col_list = ["_id", "AddressInfo.ID", "AddressInfo.AddressLine1", "AddressInfo.Latitude", "AddressInfo.Longitude"]

    df = pd.read_csv(filename, sep=",", nrows=100, usecols=col_list)
    #print(df)
    length = df.shape[0]
    #print(length)

    operator_table = Operator.query.all()

    for _, x in df.iterrows():
        if isinstance(x["AddressInfo.AddressLine1"], str) and isinstance(x["_id"], str):

            check = Station.query.filter_by(address=x["AddressInfo.AddressLine1"]).first()
            if not check:
                #print(x["AddressInfo.AddressLine1"])
                operator = random.choice(operator_table)
                new_station = Station(station_id=str(x["AddressInfo.ID"]), address=x["AddressInfo.AddressLine1"], 
                            latitude=x["AddressInfo.Latitude"], longitude=x["AddressInfo.Longitude"],
                            operator_id=operator.id)            
                this_station = new_station
                db.session.add(new_station)
                db.session.commit()
            else:
                #print(x["AddressInfo.AddressLine1"])
                this_station = check    
            check2 = Point.query.filter_by(point_id=x["_id"]).first()
            if not check2:
                #print(x['_id'])
                new_point = Point(point_id=x["_id"], station_id=this_station.id)
                db.session.add(new_point)
                db.session.commit()

    print('Points and Stations are in')            


def default_users():

    from .models import User

    for x in range(1,144):
        username = f"User{x}"
        password = f"password{x}"
        hashed_password = generate_password_hash(password, method='sha256')
        check = User.query.filter_by(username=username).first()
        if not check:
            new_user = User(public_id=str(uuid.uuid4()), username=username,
                            password=hashed_password, role="User")
            db.session.add(new_user)
            db.session.commit()

    for x in range(1,21):
        username = f"Stakeholder{x}"
        password = f"stakepassholder{x}"
        hashed_password = generate_password_hash(password, method='sha256')
        check = User.query.filter_by(username=username).first()
        if not check:
            new_user = User(public_id=str(uuid.uuid4()), username=username,
                            password=hashed_password, role="Stakeholder")
            db.session.add(new_user)
            db.session.commit()                        
    print('Default users are in')

def default_sessions(filename):

    from .models import Session, Evehicle, Point

    with open(filename) as jsdata:
        sess = json.load(jsdata)

    cont = pd.DataFrame(sess['_items'])    
    #cont = pd.read_json(filename)
    length = cont.shape[0]
    #print(cont)
    #print(length)
    #table = User.query.limit(10).all()
    #for x in range(0,10):
        #print(random.choice(table))

    ev_table = Evehicle.query.all()
    point_table = Point.query.all()

    payment_table = ["Credit_Card", "Debit_Card", "Smartphone_Wallet",
                    "Website_Payment", "QR_Code", "Cash"]

    #for x in range(0,length):
    for x in range(0,500):
        check = Session.query.filter_by(session_id=cont["_id"][x]).first()
        if not check:
            edit_start = cont["connectionTime"][x]
            year_start = edit_start[12:16]
            month_start = months_to_nums(edit_start[8:11])
            day_start = edit_start[5:7]
            time_start = edit_start[17:]
            edit_fin = cont["doneChargingTime"][x]
            year_fin = edit_fin[12:16]
            month_fin = months_to_nums(edit_fin[8:11])
            day_fin = edit_fin[5:7]
            time_fin = edit_fin[17:]
            
            begin = int(time_start[:2])*60+int(time_start[3:5])
            end = 0
            if day_start!=day_fin:
                end = 1440
            end = end + int(time_fin[:2])*60+int(time_fin[3:5])
            space = end - begin
            if space==0:
                space = 1
            rate = (cont["kWhDelivered"][x]*60)/space
            if rate < 2.0:
                protocol = "Level 1: Low"
            elif rate < 10.0:
                protocol = "Level 2: Medium"
            else:
                protocol = "Level 3: High"             
            
            ev = random.choice(ev_table)
            point = random.choice(point_table)
            payment = random.choice(payment_table)


            new_session = Session(session_id=cont["_id"][x], connection_date=year_start+month_start+day_start,
                                connection_time=time_start,  disconnection_date=year_fin+month_fin+day_fin,
                                disconnection_time=time_fin, kWh_delivered = cont["kWhDelivered"][x],
                                protocol=protocol ,payment=payment ,ev_id=ev.id, point_id=point.id)
            db.session.add(new_session)
            #print(new_session.connection_date)
            db.session.commit()
    print('Sessions are in')

def months_to_nums(x):
    
    switcher = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }
    return switcher.get(x, "???")

def initializer():
    default_admin('admin','petrol4ever')
    default_operators('echarge/backend/static/Operators_data.csv')
    default_points_stations('echarge/backend/static/points.csv')
    default_users()
    default_evs('echarge/backend/static/electric_vehicles_data.json')
    #default_sessions('echarge/backend/static/caltech_acndata_sessions_12month.json')

