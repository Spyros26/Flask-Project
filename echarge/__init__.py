from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
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
    App = Flask(__name__, static_folder='./frontend/static', template_folder='./frontend/templates')
    App.config['SECRET_KEY'] = 'hjshjhdjh'
    App.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    App.config['JSON_SORT_KEYS'] = False
    App.config['SERVER_NAME'] = 'localhost:8765'
    db.init_app(App)

    from echarge.backend import views, auth, admin, sessions

    App.register_blueprint(views, url_prefix='/evcharge/api/')
    App.register_blueprint(admin, url_prefix='/evcharge/api/')
    App.register_blueprint(auth, url_prefix='/evcharge/api/')
    App.register_blueprint(sessions, url_prefix='/evcharge/api/')

    from .models import User, RevokedToken, Evehicle, Point, Station, Operator, Session

    create_database(App)
    migrate.init_app(App, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.Login'
    login_manager.init_app(App)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    App.jinja_env.globals.update(energy_provider=energy_provider)
    App.jinja_env.globals.update(station_address=station_address)
    App.jinja_env.globals.update(round_cost=round_cost)
    App.jinja_env.globals.update(show_waiting_time=show_waiting_time)

    return App


def create_database(app):
    if not path.exists('echarge/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

def show_waiting_time(d):
    float_time = d/60000  # in minutes
    hours, seconds = divmod(float_time * 60, 3600)  # split to hours and seconds
    minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
    return [int(hours), int(minutes), int(seconds)]

def round_cost(x):
    return round(x, 2)
    
def energy_provider(point_id):
    from .models import Point, Station, Energyprovider
    point = Point.query.get(point_id)
    station = Station.query.get(point.station_id)
    provider = Energyprovider.query.get(station.provider_id)
    return provider.name

def station_address(point_id):
    from .models import Point, Station
    point = Point.query.get(point_id)
    station = Station.query.get(point.station_id)
    return station.address

    
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
    length = cont.shape[0]

    for x in range(0,500):
        check = Evehicle.query.filter_by(car_id=f"EV{x+1}").first()
        if not check:
            y = random.randint(0,length-1)
            user = User.query.filter_by(username=f"User{x+1}").first()
            new_ev = Evehicle(car_id=f"EV{x+1}", brand=cont["brand"][y], 
                        car_type=cont["type"][y], brand_id=cont["brand_id"][y],
                        model=cont["model"][y], release_year=cont["release_year"][y],
                        variant=cont["variant"][y], usable_battery_size=cont["usable_battery_size"][y],
                        ac_charger=cont["ac_charger"][y], dc_charger=cont["dc_charger"][y],
                        energy_consumption=cont["energy_consumption"][y], user_id=user.id)
            db.session.add(new_ev)
            db.session.commit()
    print('Default EVs are in')                    

def default_operators(filename):

    from .models import Operator

    df = pd.read_csv(filename, sep=";")

    for a, x in df.iterrows():
        check = Operator.query.filter_by(operator_id=x["ID"]).first()
        if not check:
            new_op = Operator(operator_id=x["ID"], name=x["Title"], 
                        website=x["WebsiteURL"], email=x["ContactEmail"])            
            db.session.add(new_op)
            db.session.commit()
    print('Default operators are in') 

    
def default_points_stations(filename):

    from .models import Station, Point, Operator, Energyprovider
    
    col_list = ["_id", "AddressInfo.ID", "AddressInfo.Title", "AddressInfo.AddressLine1", "AddressInfo.Latitude", "AddressInfo.Longitude", "AddressInfo.ContactTelephone1", "AddressInfo.ContactEmail", "AddressInfo.RelatedURL"]

    df = pd.read_csv(filename, sep=",", nrows=1000, usecols=col_list)
    #df = pd.read_csv(filename, sep=",", usecols=col_list)

    operator_table = Operator.query.all()
    provider_table = Energyprovider.query.all()

    for _, x in df.iterrows():
        if isinstance(x["AddressInfo.AddressLine1"], str) and isinstance(x["AddressInfo.Title"], str) and isinstance(x["_id"], str):

            check = Station.query.filter_by(address=x["AddressInfo.AddressLine1"]).first()
            if not check:
                phone = x["AddressInfo.ContactTelephone1"]

                mail = x["AddressInfo.ContactEmail"]

                site = x["AddressInfo.RelatedURL"]

                operator = random.choice(operator_table)
                provider = random.choice(provider_table)
                new_station = Station(station_id=str(x["AddressInfo.ID"]), 
                                name=x["AddressInfo.Title"], email=mail, 
                                phone=phone, website=site, address=x["AddressInfo.AddressLine1"], 
                                latitude=x["AddressInfo.Latitude"], longitude=x["AddressInfo.Longitude"],
                                operator_id=operator.id, provider_id=provider.id)            
                this_station = new_station
                db.session.add(new_station)
                db.session.commit()
            else:
                this_station = check    
            check2 = Point.query.filter_by(point_id=x["_id"]).first()
            if not check2:
                new_point = Point(point_id=x["_id"], station_id=this_station.id)
                db.session.add(new_point)
                db.session.commit()

    print('Points and Stations are in')            


def default_users():
    from .models import User
    names = ["Liam", "Olivia", "Noah",	"Emma", "Oliver", "Ava", "William", "Sophia", "Elijah", "Isabella", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Mia", "Mason", "Harper", "Ethan", "Evelyn"]
    for x in range(1,501):
        username = f"User{x}"
        password = f"password{x}"
        name = names[x % 20]
        email = f"User{x}@gmail.com"
        hashed_password = generate_password_hash(password, method='sha256')
        check = User.query.filter_by(username=username).first()
        if not check:
            new_user = User(public_id=str(uuid.uuid4()), username=username,
                            password=hashed_password, name=name, email=email, role="User")
            db.session.add(new_user)
            db.session.commit()

    for x in range(1,21):
        username = f"Privileged{x}"
        password = f"privypass{x}"
        name = "Privileged Stakeholder"
        email = f"Privileged{x}@gmail.com"
        hashed_password = generate_password_hash(password, method='sha256')
        check = User.query.filter_by(username=username).first()
        if not check:
            new_user = User(public_id=str(uuid.uuid4()), username=username,
                            password=hashed_password, name=name, email=email, role="Privileged")
            db.session.add(new_user)
            db.session.commit()                        
    print('Default users are in')

def default_sessions(filename):

    from .models import Session, Evehicle, Point

    with open(filename) as jsdata:
        sess = json.load(jsdata)

    cont = pd.DataFrame(sess['_items'])    

    ev_table = Evehicle.query.all()
    point_table = Point.query.all()

    payment_table = ["Credit_Card", "Debit_Card", "Smartphone_Wallet",
                    "Website_Payment", "QR_Code", "Cash"]

    for x in range(0,len(cont)):
        check = Session.query.filter_by(session_id=cont["_id"][x]).first()
        if not check and isinstance(cont["connectionTime"][x], str) and isinstance(cont["doneChargingTime"][x], str) and isinstance(cont["disconnectTime"][x], str):
            edit_start = cont["connectionTime"][x]
            
            year_start = edit_start[12:16]
            month_start = months_to_nums(edit_start[8:11])
            day_start = edit_start[5:7]
            time_start = edit_start[17:19]+edit_start[20:22]+edit_start[23:25]

            edit_fin = cont["doneChargingTime"][x]
            year_fin = edit_fin[12:16]
            month_fin = months_to_nums(edit_fin[8:11])
            day_fin = edit_fin[5:7]
            time_fin = edit_fin[17:19]+edit_fin[20:22]+edit_fin[23:25]
            
            edit_dis = cont["disconnectTime"][x]
            year_dis = edit_dis[12:16]
            month_dis = months_to_nums(edit_dis[8:11])
            day_dis = edit_dis[5:7]
            time_dis = edit_dis[17:19]+edit_dis[20:22]+edit_dis[23:25]

            begin = int(time_start[:2])*60+int(time_start[2:4])
            end = 0
            if day_start!=day_fin:
                end = 1440
            end = end + int(time_fin[:2])*60+int(time_fin[2:4])
            space = end - begin
            if space==0:
                space = 1
            rate = (cont["kWhDelivered"][x]*60)/space
            if rate < 5.0:
                protocol = "Level 1: Low"
            elif rate < 25.0:
                protocol = "Level 2: Medium"
            else:
                protocol = "Level 3: High"             
            
            ev = random.choice(ev_table)
            point = random.choice(point_table)
            payment = random.choice(payment_table)


            new_session = Session(session_id=cont["_id"][x], connection_date=year_start+month_start+day_start,
                                connection_time=time_start,  done_date=year_fin+month_fin+day_fin,
                                done_time=time_fin, disconnection_date=year_dis+month_dis+day_dis,
                                disconnection_time=time_dis, kWh_delivered = cont["kWhDelivered"][x],
                                protocol=protocol ,payment=payment ,ev_id=ev.id, point_id=point.id)
            db.session.add(new_session)
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

def default_providers():

    from .models import Energyprovider

    us_table = [
        "4Change Energy",
        "AEP Energy",
        "Ambit energy",
        "Amigo Energy",
        "Beyond Power",
        "Bounce Energy",
        "Champion Energy Services",
        "Cirro Energy",
        "Constellation",
        "CPL Retail Energy",
        "Direct Energy",
        "FirstEnergy Solutions",
        "First Choice Power",
        "Gexa Energy",
        "Green Mountain Energy",
        "IGS Energy",
        "Infinite Energy",
        "Inspire Energy",
        "Just Energy",
        "Liberty Power",
        "North American Power",
        "Pennywise Power",
        "StarTex Power",
        "TriEagle Energy",
        "WGL Energy"
    ]
    for x in range(0,len(us_table)):
        prov = Energyprovider.query.filter_by(name=us_table[x]).first()
        if not prov:
            new_provider = Energyprovider(provider_id=f"0987654321{x+1}", name=us_table[x])
            db.session.add(new_provider)
            db.session.commit()
    print("Default providers are in!")    


def initializer():
    default_admin('admin','petrol4ever')
    default_providers()
    default_operators('echarge/backend/static/Operators_data.csv')
    default_points_stations('echarge/backend/static/points1.csv')
    #default_points_stations('echarge/backend/static/points2.csv')
    default_users()
    default_evs('echarge/backend/static/electric_vehicles_data.json')
    default_sessions('echarge/backend/static/caltech_acndata_sessions_12month.json')

