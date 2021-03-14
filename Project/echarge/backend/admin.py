from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response, make_response
from ..models import User, Session, Evehicle, Point
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, default_admin, months_to_nums
import uuid
import json
import pandas as pd
from .auth import token_required
import random
import os
import flask_csv as fcsv

admin = Blueprint('admin', __name__)

@admin.route('/admin/usermod/<username>/<password>/<role>', methods=['POST'])
@token_required
def usermod(current_user, username, password, role):
    if current_user.role != "Admin":
        return make_response('Not allowed to perform this action!', 401)

    user = User.query.filter_by(username=username).first()

    hashed_password = generate_password_hash(password, method='sha256')

    if not user:
        new_user = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return make_response('New stakeholder successfully created!')
    
    user.password = hashed_password
    user.role = role
    db.session.commit()

    return make_response('Stakeholder\'s password/role updated successfully!')


@admin.route('/admin/users/<username>', methods=['GET'])
@token_required
def users(current_user, username):
    if current_user.role != "Admin":
        return make_response('Not allowed to perform this action!', 401)

    askformat = request.args.get('format', default='json', type=str)
    if askformat!='json' and askformat!='csv':
        return make_response('Cannot accept format. Supported formats are json (default) and csv.', 400)

    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response('The user was not found!', 400)

    if askformat=='json':
        return jsonify({'username' : user.username, 'hashed_password' : user.password, 'name' : user.name, 'email' : user.email, 'role' : user.role})

    else:
        return fcsv.send_csv([{'username' : user.username, 'hashed_password' : user.password, 'name' : user.name, 'email' : user.email, 'role' : user.role}], 
                                "reply.csv", ["username", "hashed_password", "name", "email", "role"], delimiter=';')

@admin.route('/admin/healthcheck', methods=['GET'])
@token_required
def healthcheck(current_user):
    if current_user.role != "Admin":
        return make_response('Not allowed to perform this action!', 401)

    try:
        cnt = User.query.count()
        return jsonify({'status' : 'OK'})
    except:
        return jsonify({'status' : 'failed'}), 400


@admin.route('/admin/resetsessions', methods=['POST'])
@token_required
def resetsessions(current_user):
    if current_user.role != "Admin":
        return make_response('Not allowed to perform this action!', 401)

    try:
        num_sessions_deleted = db.session.query(Session).delete()
        db.session.commit()
        default_admin('admin','petrol4ever')
        return jsonify({'status' : 'OK'})
    except:
        return jsonify({'status' : 'failed'}), 400


@admin.route('/admin/system/sessionsupd', methods=['POST'])
@token_required
def sessions_update(current_user):
    if current_user.role != "Admin":
        return make_response('Not allowed to perform this action!', 401)

    askformat = request.args.get('format', default='json', type=str)
    if askformat!='json' and askformat!='csv':
        return make_response('Cannot accept format. Supported formats are json (default) and csv.', 400)

    filename = request.form.get('file')
    if filename.endswith("json"):
        with open(filename) as jsdata:
            sess = json.load(jsdata)
        
        try:
            cont = pd.DataFrame(sess['_items'])
            length = cont.shape[0]    
            sessions_imported = 0
            sessions_in_db = 0

            ev_table = Evehicle.query.all()
            point_table = Point.query.all()

            payment_table = ["Credit_Card", "Debit_Card", "Smartphone_Wallet",
                            "Website_Payment", "QR_Code", "Cash"]

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
                    db.session.commit()
                    sessions_imported = sessions_imported + 1
            
            sessions_in_db = Session.query.count()

            if askformat=='json':
                return jsonify({'SessionsInUploadedFile' : length,
                                'SessionsImported' : sessions_imported,
                                'TotalSessionsInDatabase' : sessions_in_db})
            else:
                return fcsv.send_csv([{'SessionsInUploadedFile' : length,
                                'SessionsImported' : sessions_imported,
                                'TotalSessionsInDatabase' : sessions_in_db}], "reply.csv",
                                ["SessionsInUploadedFile", "SessionsImported", "TotalSessionsInDatabase"], delimiter=';')
        except:
                return make_response('Data in this file are not in the supported format. Please try again with a file with valid data.', 400)                       

    else:
        return make_response('Cannot accept this file type. Supported file type is json', 400)                        