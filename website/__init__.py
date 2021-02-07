from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

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
