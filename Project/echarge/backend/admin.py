from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response, make_response
from ..models import User, ChargingSession
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, default_admin
import uuid
from .auth import token_required

admin = Blueprint('admin', __name__)

@admin.route('/admin/usermod/<username>/<password>', methods=['POST'])
@token_required
def usermod(current_user, username, password):
    if not current_user.is_admin:
        return jsonify({'message' : 'Not allowed to perform this action!'})

    user = User.query.filter_by(username=username).first()

    hashed_password = generate_password_hash(password, method='sha256')

    if not user:
        new_user = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password, is_admin=False)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message' : 'New user successfully created!'})

    user.password = hashed_password
    db.session.add(user)
    db.session.commit()

    return jsonify({'message' : 'User password changed successfully!'})


@admin.route('/admin/users/<username>', methods=['GET'])
@token_required
def users(current_user, username):
    if not current_user.is_admin:
        return jsonify({'message' : 'Not allowed to perform this action!'})

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'message' : 'The user was not found!'})

    return jsonify({'Username' : user.username, 'hashed_password' : user.password, 'is_admin' : user.is_admin, 'sessions' : user.charging_sessions})


@admin.route('/admin/healthcheck', methods=['GET'])
@token_required
def healthcheck(current_user):
    if not current_user.is_admin:
        return jsonify({'message' : 'Not allowed to perform this action!'})

    try:
        cnt = User.query.count()
        success = True
    except:
        success = False

    if success:
        return jsonify({'status' : 'OK'})

    return jsonify({'status' : 'failed'})


@admin.route('/admin/resetsessions', methods=['POST'])
@token_required
def resetsessions(current_user):
    if not current_user.is_admin:
        return jsonify({'message' : 'Not allowed to perform this action!'})

    try:
        num_sessions_deleted = db.session.query(ChargingSession).delete()
        db.session.commit()
        default_admin('admin','petrol4ever')
        success = True
    except:
        success = False

    if success:
        return jsonify({'status' : 'OK'})

    return jsonify({'status' : 'failed'})