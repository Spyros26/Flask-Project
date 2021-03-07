from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import current_user
from .auth import token_required
from ..models import Session
from .. import db
import json

views = Blueprint('views', __name__)

"""
@views.route('/', methods=['GET', 'POST'])
@token_required
def home(current_user):
    if request.method == 'POST':
        charging_program = request.form.get('charging_program')
        EV = request.form.get('EV')

        if len(EV) < 5:
            flash('EV is invalid', category='error')
        elif len(charging_program) > 2:
            flash('The Charging Program you selected does not exist!', category='error')
        else:
            new_charging_session = ChargingSession(EV=EV, charging_program=charging_program, user_id=current_user.id)
            db.session.add(new_charging_session)
            db.session.commit()
            flash('Wait for charging process!', category='success')
            return redirect(url_for('views.charging'))
    
    return render_template("home.html", user=current_user)


@views.route('/charging', methods=['GET', 'POST'])
@token_required
def charging(current_user):
    if request.method == 'POST':
        flash('Charging stopped!', category='success')
        return redirect(url_for('views.home'))

    return render_template("charging.html", user=current_user)


@views.route('/issue-statement', methods=['GET', 'POST'])
@token_required
def view_sessions(current_user):
    if request.method == 'POST':
        flash('The statement has been successfully issued!', category='success')
        return redirect(url_for('views.home'))

    return render_template("view_sessions.html", user=current_user)


@views.route('/delete-session', methods=['POST'])
def delete_session():
    session = json.loads(request.data)
    sessionId = session['sessionId']
    session = ChargingSession.query.get(sessionId)
    if session:
        if session.user_id == current_user.id:
            db.session.delete(session)
            db.session.commit()

    return jsonify({})

"""

