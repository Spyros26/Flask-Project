from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from .models import User, RevokedToken
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

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
            return jsonify({'message' : 'Token not found!'}), 400

        if invalid:
            return jsonify({'message' : 'Invalid Token!'}), 400 

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
            return jsonify({'message' : 'Token not found!'}), 400

        if invalid:
            return jsonify({'message' : 'Invalid Token!'}), 400 

        try:
            data = jwt.decode(token, 'hjshjhdjh')
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Invalid Token!'}), 400

        return f(current_user, *args, **kwargs)

    return decorated                     

@auth.route('/login', methods=['GET', 'POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return render_template('login.html', user=current_user)
  
    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return render_template('login.html', user=current_user)

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 'hjshjhdjh')
        res = token.decode('UTF-8')
        return jsonify({'token' : res})
        #response = make_response(render_template('login.html'))
        #response.headers['X-OBSERVATORY-AUTH'] = res
        return response

    return render_template('login.html', user=current_user)    

@auth.route('/admin/usermod/<new_username>/<new_password>', methods=['POST'])
@token_required
def usermod(current_user, new_username, new_password):
    if not current_user.admin:
        return jsonify({'message' : 'Not allowed to perform this action!'})

    check = User.query.filter_by(username=new_username).first()

    hashed_password = generate_password_hash(new_password, method='sha256')

    if not check:
        new_user = User(public_id=str(uuid.uuid4()), username=new_username, password=hashed_password, admin=False)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message' : 'New user successfully created!'})

    check.password = hashed_password
    db.session.add(check)
    db.session.commit()

    return jsonify({'message' : 'User password changed successfully!'})

@auth.route('/logout', methods=['POST'])
@token_made_black
def logout(token):
    black_token = RevokedToken(token=token)
    db.session.add(black_token)
    db.session.commit()

    return jsonify({'message' : 'You have logged out!'})


