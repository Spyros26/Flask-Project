from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response, make_response
from ..models import User, RevokedToken
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

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

@auth.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response('Could not verify', 400, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 'hjshjhdjh')
        res = token.decode('UTF-8')
        return jsonify({'token' : res})

    return make_response('Could not verify', 400, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


@auth.route('/logout', methods=['POST'])
@token_made_black
def logout(token):
    black_token = RevokedToken(token=token)
    db.session.add(black_token)
    db.session.commit()

    return Response(status=200)


