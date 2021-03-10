from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models import Session, User, Evehicle, Point
from .. import db
import json, uuid, random
from datetime import datetime, date, timedelta

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
            disconnection_time = (datetime.now() + timedelta(seconds=int(float(kWh_Requested)*3600/rate))).strftime("%H%M%S")
            
            new_charging_session = Session(session_id=str(uuid.uuid4()), connection_date=date.today(), connection_time=connection_time, disconnection_time=disconnection_time, kWh_delivered=float(kWh_Requested), protocol=protocol, payment=payment, point_id=point.id, ev_id=car.id)
            db.session.add(new_charging_session)
            db.session.commit()
            flash('Wait for charging process!', category='success')
            return redirect(url_for('views.charging', sessionID=new_charging_session.session_id))
    
    return render_template("home.html", user=current_user)


@views.route('/charging/<sessionID>', methods=['GET', 'POST'])
@login_required
def charging(sessionID):
    if request.method == 'POST':
        current_session = Session.query.filter_by(session_id=sessionID).first()
        current_session.disconnection_date = date.today()
        if current_session.disconnection_time > datetime.now().strftime("%H%M%S"):
            current_session.kWh_delivered = current_session.kWh_delivered*(int(datetime.now().strftime("%H%M%S"))-int(current_session.connection_time))/(int(current_session.disconnection_time)-int(current_session.connection_time))
            current_session.disconnection_time = datetime.now().strftime("%H%M%S")
        db.session.commit()
        flash('Charging stopped!', category='success')
        return redirect(url_for('views.home'))

    return render_template("charging.html", user=current_user)


@views.route('/issue-statement', methods=['GET', 'POST'])
@login_required
def view_sessions():
    if request.method == 'POST':
        flash('The statement has been successfully issued!', category='success')
        return redirect(url_for('views.home'))

    return render_template("view_sessions.html", user=current_user)


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



