from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models import Session, User, Evehicle, Point
from .. import db
import json, uuid, random
from datetime import datetime, date, timedelta
from .sessions import sort_criteria

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        car_id = request.form.get('car_id')
        kWh_Requested = request.form.get('kWh_Requested')
        protocol = request.form.get('protocol')
        payment = request.form.get('payment')
        point_id = request.form.get('point')

        car = Evehicle.query.filter_by(car_id=car_id).first()
        point = Point.query.filter_by(point_id=point_id).first()

        if car not in current_user.evs:
            flash('Car id is invalid!', category='error')
        elif protocol not in ["Level 1: Low", "Level 2: Medium", "Level 3: High"]:
            flash('Protocol is invalid!', category='error')
        elif payment not in ["Credit_Card", "Debit_Card", "Smartphone_Wallet", "Website_Payment", "QR_Code", "Cash"]:
            flash('Payment Method is invalid!', category='error')
        elif not point:
            flash('Point id is invalid!', category='error')
        else:
            if protocol == "Level 1: Low":
                rate = random.uniform(2.0, 5.0)
            elif protocol == "Level 2: Medium":
                rate = random.uniform(10.0, 25.0)
            elif protocol == "Level 3: High":
                rate = random.uniform(40.0, 60.0)

            connection_time = datetime.now().strftime("%H%M%S")
            connection_date = datetime.now().strftime("%Y%m%d")
            done_time = (datetime.now() + timedelta(seconds=int(float(kWh_Requested)*3600/rate))).strftime("%H%M%S")
            done_date = (datetime.now() + timedelta(seconds=int(float(kWh_Requested)*3600/rate))).strftime("%Y%m%d")
            
            new_charging_session = Session(session_id=str(uuid.uuid4()), connection_date=connection_date, connection_time=connection_time, done_date=done_date, done_time=done_time, disconnection_date="??????", disconnection_time="??????", kWh_delivered=float(kWh_Requested), protocol=protocol, payment=payment, point_id=point.id, ev_id=car.id)
            db.session.add(new_charging_session)
            db.session.commit()
            flash('Wait for charging process!', category='success')
            return redirect(url_for('views.charging', sessionID=new_charging_session.session_id))
    
    return render_template("home.html", user=current_user)


@views.route('/charging/<sessionID>', methods=['GET', 'POST'])
@login_required
def charging(sessionID):
    current_session = Session.query.filter_by(session_id=sessionID).first()
    if request.method == 'POST':
        current_session.disconnection_date = (datetime.now()).strftime("%Y%m%d")
        current_session.disconnection_time = (datetime.now()).strftime("%H%M%S")
        if current_session.disconnection_time < current_session.done_time and current_session.disconnection_date <= current_session.done_date:
            current_session.kWh_delivered = current_session.kWh_delivered*(int(datetime.now().strftime("%H%M%S"))-int(current_session.connection_time))/(int(current_session.done_time)-int(current_session.connection_time))
            current_session.done_time = datetime.now().strftime("%H%M%S")
            current_session.done_date = current_session.disconnection_date
        db.session.commit()
        flash('Charging stopped!', category='success')
        return redirect(url_for('views.home'))

    FMT = '%H%M%S'
    tdelta = datetime.strptime(current_session.done_time, FMT) - datetime.strptime(current_session.connection_time, FMT)
    if tdelta.days < 0:
        tdelta = timedelta(days=0, seconds=tdelta.seconds, microseconds=tdelta.microseconds)
    duration = round(tdelta.total_seconds()/60, 2)

    return render_template("charging.html", user=current_user, duration=duration)


@views.route('/issue-statement/<datefrom>/<dateto>', methods=['GET', 'POST'])
@login_required
def view_sessions(datefrom, dateto):
    if request.method == 'POST':
        flash('The statement has been successfully issued!', category='success')
        return redirect(url_for('views.home'))
    
    sessions = []
    datefrom = datefrom[:4] + datefrom[5:7] + datefrom[8:]
    dateto = dateto[:4] + dateto[5:7] + dateto[8:]

    for i in range(len(current_user.evs)):
        pool = Session.query.filter((Session.ev_id==current_user.evs[i].id) & (Session.connection_date>=datefrom) & (Session.done_date<=dateto)).all()
        sessions = sessions + pool
    sessions.sort(key=sort_criteria)      
    return render_template("view_sessions.html", user=current_user, sessions=sessions)


@views.route('/statement_filters', methods=['GET', 'POST'])
@login_required
def statement_filters():
    if request.method == 'POST':
        datefrom = request.form.get('datefrom')
        dateto = request.form.get('dateto')
        if not datefrom or not dateto:
            flash('Select filters', category='error')
        else:
            flash('Statement filters have been applied!', category='success')
        return redirect(url_for('views.view_sessions', datefrom=datefrom, dateto=dateto))
         
    return render_template("statement_filters.html", user=current_user)


@views.route('/delete-session', methods=['POST'])
def delete_session():
    session = json.loads(request.data)
    sessionId = session['sessionId']
    session = Session.query.get(sessionId)
    ev = Evehicle.query.get(session.ev_id)
    if session:
        if ev.user_id == current_user.id:
            db.session.delete(session)
            db.session.commit()

    return jsonify({})



