from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response, make_response
from ..models import User, RevokedToken, Evehicle
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from flask_login import login_user, login_required, logout_user, current_user
import uuid
import jwt
import datetime
from functools import wraps


auth = Blueprint('auth', __name__)

def token_made_black(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'X-OBSERVATORY-AUTH' in request.headers:
            token = request.headers['X-OBSERVATORY-AUTH']

        invalid = RevokedToken.query.filter_by(token=token).first()

        if not token:
            return make_response('Token not found', 400)

        if invalid:
            return make_response('Invalid Token', 400) 

        return f(token, *args, **kwargs)

    return decorated

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'X-OBSERVATORY-AUTH' in request.headers:
            token = request.headers['X-OBSERVATORY-AUTH']

        invalid = RevokedToken.query.filter_by(token=token).first()

        if not token:
            return make_response('Token not found', 400)

        if invalid:
            return make_response('Invalid Token', 400)

        try:
            data = jwt.decode(token, 'hjshjhdjh')
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return make_response('Invalid Token', 400)

        return f(current_user, *args, **kwargs)

    return decorated                     

@auth.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response('Could not verify', 400)

    if check_password_hash(user.password, password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 'hjshjhdjh')
        res = token.decode('UTF-8')
        return jsonify({'token' : res})

    return make_response('Could not verify', 400)


@auth.route('/logout', methods=['POST'])
@token_made_black
def logout(token):
    try:
        black_token = RevokedToken(token=token)
        db.session.add(black_token)
        db.session.commit()
        return Response(status=200)
    except:
        return Response(status=402)


@auth.route('/Login', methods=['GET', 'POST'])
def Login():
    status=200
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
                status=400
        else:
            flash('User does not exist.', category='error')
            status=400

    return render_template("login.html", user=current_user), status


@auth.route('/Logout')
@login_required
def Logout():
    logout_user()
    return redirect(url_for('auth.Login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    status=200
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('Name')
        email = request.form.get('email')
        car_brand = request.form.get('car_brand')
        car_model = request.form.get('car_model')
        car_id = request.form.get('car_id')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        ev = Evehicle.query.filter_by(car_id=car_id).first()
        user = User.query.filter_by(username=username).first()
        if ev:
            flash('EV already exists.', category='error')
            status=400 
        elif user:
            flash('Username already exists.', category='error')
            status=400
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
            status=400
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
            status=400
        elif len(car_brand) < 2:
            flash('Car Brand must be greater than 1 character.', category='error')
            status=400
        elif len(car_model) < 2:
            flash('Car Model must be greater than 1 character.', category='error')
            status=400
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
            status=400
        elif len(password1) < 4:
            flash('Password must be at least 4 characters.', category='error')
            status=400
        else:
            new_user = User(username=username, password=generate_password_hash(
                password1, method='sha256'), name=name, email=email, role="User")
            db.session.add(new_user)
            db.session.commit()
            new_ev = Evehicle(car_id=car_id, brand=car_brand, model=car_model, user_id=new_user.id)
            db.session.add(new_ev)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user), status

