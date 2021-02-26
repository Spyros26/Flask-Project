from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import uuid
from werkzeug.security import generate_password_hash
import pandas as pd
import json

db = SQLAlchemy()
DB_NAME = "Data.db"


def create_app():
    App = Flask(__name__)
    App.config['SECRET_KEY'] = 'hjshjhdjh'
    App.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(App)

    from .views import views
    from .auth import auth

    App.register_blueprint(views, url_prefix='/')
    App.register_blueprint(auth, url_prefix='/')

    from .models import User, ChargingSession

    create_database(App)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(App)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    return App


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

def default_admin(username, password):

    from .models import User
    user = User.query.filter_by(username=username).first()
    if not user:
        hashed_password = generate_password_hash(password, method='sha256')
        admin = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password, admin=True)
        db.session.add(admin)
        db.session.commit()
        print('Default admin created!')
    else:
        user.password = generate_password_hash(password, method='sha256')
        db.session.add(user)
        db.session.commit()
        print('Default admin initialized')

def default_evs(filename):
    
    from .models import EVehicle

    with open(filename) as jsdata:
        evs = json.load(jsdata)

    cont = pd.DataFrame(evs['data'])    
    #cont = pd.read_json(filename)
    length = cont.shape[0]
    #print(cont)
    #print(length)
    for x in range(0,length):
        check = EVehicle.query.filter_by(car_id=cont["id"][x]).first()
        if not check:
            new_ev = EVehicle(car_id=cont["id"][x], brand=cont["brand"][x], 
                        car_type=cont["type"][x], brand_id=cont["brand_id"][x],
                        model=cont["model"][x], release_year=cont["release_year"][x],
                        variant=cont["variant"][x], usable_battery_size=cont["usable_battery_size"][x],
                        ac_charger=cont["ac_charger"][x], dc_charger=cont["dc_charger"][x],
                        energy_consumption=cont["energy_consumption"][x])
            db.session.add(new_ev)
            db.session.commit()            
