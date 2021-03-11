from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response, make_response
from ..models import User, Session, Evehicle, Point
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, default_admin, months_to_nums
import uuid
import json
import pandas as pd
from .auth import token_required
import random

admin = Blueprint('admin', __name__)

@admin.route('/admin/usermod/<username>/<password>', methods=['POST'])
@token_required
def usermod(current_user, username, password):
    if current_user.role != "Admin":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    user = User.query.filter_by(username=username).first()

    hashed_password = generate_password_hash(password, method='sha256')

    if not user:
        new_user = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password, role="User")
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
    if current_user.role != "Admin":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'message' : 'The user was not found!'})

    return jsonify({'username' : user.username, 'hashed_password' : user.password, 'role' : user.role})


@admin.route('/admin/healthcheck', methods=['GET'])
@token_required
def healthcheck(current_user):
    if current_user.role != "Admin":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    try:
        cnt = User.query.count()
        return jsonify({'status' : 'OK'})
    except:
        return jsonify({'status' : 'failed'})


@admin.route('/admin/resetsessions', methods=['POST'])
@token_required
def resetsessions(current_user):
    if current_user.role != "Admin":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    try:
        num_sessions_deleted = db.session.query(Session).delete()
        db.session.commit()
        default_admin('admin','petrol4ever')
        return jsonify({'status' : 'OK'})
    except:
        return jsonify({'status' : 'failed'})


@admin.route('/admin/system/sessionsupd', methods=['POST'])
@token_required
def sessions_update(current_user):
    if current_user.role != "Admin":
        return jsonify({'message' : 'Not allowed to perform this action!'})


    filename = request.form.get('file')
    with open(filename) as jsdata:
        sess = json.load(jsdata)

    cont = pd.DataFrame(sess['_items'])
    length = cont.shape[0]    
    sessions_imported = 0
    sessions_in_db = 0

    ev_table = Evehicle.query.all()
    point_table = Point.query.all()

    payment_table = ["Credit_Card", "Debit_Card", "Smartphone_Wallet",
                    "Website_Payment", "QR_Code", "Cash"]

    #for x in range(0,length):
    for x in range(500,1000):
        check = Session.query.filter_by(session_id=cont["_id"][x]).first()
        if not check:
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
            #print(new_session.connection_date)
            db.session.commit()
            sessions_imported = sessions_imported + 1
    
    sessions_in_db = Session.query.count()
    return jsonify({'SessionsInUploadedFile' : length,
                    'SessionsImported' : sessions_imported,
                    'TotalSessionsInDatabase' : sessions_in_db})
