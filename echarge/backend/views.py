from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..models import Session, User, Evehicle, Point, Station
from .. import db
import json, uuid, random
from datetime import datetime, date, timedelta
from .sessions import sort_criteria


views = Blueprint('views', __name__)

def cost_rate(protocol):
    if protocol =="Level 1: Low":
        return 1
    elif protocol =="Level 2: Medium":
        return 2
    return 3

def station_cords():
    reply = []
    stationlist = Station.query.all()
    for station in stationlist:
        if isinstance(station.website, str) and len(station.website)>5:
            reply.append({'type': 'Feature',
            'properties': {
                'description': 
                f'<strong>{station.name}</strong><p> <br> Address: {station.address} <br> Number of charging points: {len(station.points)} <br> Point Ids List: {[x.point_id for x in station.points]} <br> Telephone: {station.phone} <br> E-mail: {station.email} <br> Website: <a href={station.website} target="_blank" title="Opens in a new window">{station.website}</a></p>',
                'icon': 'charging-station'
                },
            'geometry': {
                'type': 'Point',
                'coordinates': [float(station.longitude), float(station.latitude)]
            }
        })
        else:
            reply.append({'type': 'Feature',
            'properties': {
                'description': 
                f'<strong>{station.name}</strong><p> <br> Address: {station.address} <br> Number of charging points: {len(station.points)} <br> Point Ids List: {[x.point_id for x in station.points]} <br> Telephone: {station.phone} <br> E-mail: {station.email}</p>',
                'icon': 'charging-station'
                },
            'geometry': {
                'type': 'Point',
                'coordinates': [float(station.longitude), float(station.latitude)]
            }
        })


    return reply

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    status=200
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
            status=400
        elif protocol not in ["Level 1: Low", "Level 2: Medium", "Level 3: High"]:
            flash('Protocol is invalid!', category='error')
            status=400
        elif payment not in ["Credit_Card", "Debit_Card", "Smartphone_Wallet", "Website_Payment", "QR_Code", "Cash"]:
            flash('Payment Method is invalid!', category='error')
            status=400
        elif not point:
            flash('Point id is invalid!', category='error')
            status=400
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
    
    return render_template("home.html", user=current_user), status


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

    connection = 1000*int(datetime(int(current_session.connection_date[:4]), int(current_session.connection_date[4:6]), int(current_session.connection_date[6:8]), int(current_session.connection_time[:2]), int(current_session.connection_time[2:4]), int(current_session.connection_time[4:6]) ).timestamp()) 
    FMT = '%H%M%S'
    tdelta = datetime.strptime(current_session.done_time, FMT) - datetime.strptime(current_session.connection_time, FMT)
    if tdelta.days < 0:
        tdelta = timedelta(days=0, seconds=tdelta.seconds, microseconds=tdelta.microseconds)
    duration = round(tdelta.total_seconds()/60, 2)
    return render_template("charging.html", user=current_user, duration=duration, session=current_session, connection=connection)


@views.route('/issue-statement/<datefrom>/<dateto>', methods=['GET', 'POST'])
@login_required
def view_sessions(datefrom, dateto):
    if request.method == 'POST':
        if request.form.get("opta"):
            flash('The statement has been successfully issued!', category='success')
            return redirect(url_for('views.home'))
        elif request.form.get("optb"):
            return redirect(url_for('views.chart', datefrom=datefrom, dateto=dateto))
    
    sessions = []
    date_from = datefrom[:4] + datefrom[5:7] + datefrom[8:]
    date_to = dateto[:4] + dateto[5:7] + dateto[8:]

    for i in range(len(current_user.evs)):
        pool = Session.query.filter((Session.ev_id==current_user.evs[i].id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
        sessions = sessions + pool
    sessions.sort(key=sort_criteria)      
    return render_template("view_sessions.html", user=current_user, sessions=sessions, datefrom=datefrom, dateto=dateto)


@views.route('/statement_filters', methods=['GET', 'POST'])
@login_required
def statement_filters():
    status=200
    if request.method == 'POST':
        datefrom = request.form.get('datefrom')
        dateto = request.form.get('dateto')
        if not datefrom or not dateto:
            flash('Select filters', category='error')
            status=400
        else:
            flash('Statement filters have been applied!', category='success')
            return redirect(url_for('views.view_sessions', datefrom=datefrom, dateto=dateto))
         
    return render_template("statement_filters.html", user=current_user), status


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

@views.route('/find_station_near_you', methods=['GET'])
def my_maps():

    mapbox_access_token = 'pk.eyJ1IjoidGhhbm9zYmIzIiwiYSI6ImNrbTduZGEwYzBrb2cyb2xhOXI5MXowcnEifQ.Yj-JHpwSZreC1Z1-FVhIsA'

    return render_template('map_index.html', user = current_user, mapbox_access_token=mapbox_access_token, POIs=station_cords())

@views.route('/chart/<datefrom>/<dateto>', methods=['GET', 'POST'])
@login_required
def chart(datefrom, dateto):
    if request.method == 'POST':
        if request.form.get("back"):
            return redirect(url_for('views.view_sessions', datefrom=datefrom, dateto=dateto))
        elif request.form.get("plot"):
            y = request.form.get('axis_y')
            x = request.form.get('axis_x')
            sessions = []
            date_from = datefrom[:4] + datefrom[5:7] + datefrom[8:]
            date_to = dateto[:4] + dateto[5:7] + dateto[8:]

            #startdate = datefrom[8:] + "/" + datefrom[5:7] + "/" + datefrom[:4]

            for i in range(len(current_user.evs)):
                pool = Session.query.filter((Session.ev_id==current_user.evs[i].id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
                sessions = sessions + pool
            sessions.sort(key=sort_criteria)
            
            hor = []
            ver = []

            if x=="Index":
                temp = 1
                for item in sessions:
                    hor.append(temp)
                    temp = temp + 1

                money_spent = 0
                kwh = 0
                if y=="total_money":
                    for item in sessions:
                        money_spent = round(money_spent + cost_rate(item.protocol)*0.15*item.kWh_delivered, 2)
                        ver.append(money_spent)

                    title = "Total Money Paid for Sessions"    

                elif y=="money":
                    for item in sessions:
                        ver.append(round(cost_rate(item.protocol)*0.15*item.kWh_delivered,2))
                    title = "Money Paid for Each Session"        

                elif y=="total_kwh":
                    for item in sessions:
                        kwh = round(kwh + item.kWh_delivered, 2)
                        ver.append(kwh)
                    title = "Total KWh Delivered during Sessions"    

                else:
                    for item in sessions:
                        ver.append(round(item.kWh_delivered, 2))
                    title = "KWh Delivered during Each Session"                        


            else:
                item = sessions[0]
                check = item.connection_date[6:8]+"/"+item.connection_date[4:6]+"/"+item.connection_date[:4]
                hor.append(check)
                for item in sessions:
                    new = item.connection_date[6:8]+"/"+item.connection_date[4:6]+"/"+item.connection_date[:4]
                    if check!=new:
                        hor.append(new)
                        check = new

                money_spent = 0
                kwh = 0
                index = 0
                check = "0"

                if y=="total_money":

                    for item in sessions:
                        money_spent = round(money_spent + cost_rate(item.protocol)*0.15*item.kWh_delivered, 2)

                        if check!=item.connection_date:
                            ver.append(money_spent)
                            if check!="0":
                                index = index + 1
                            check = item.connection_date
                        else:
                            ver[index] = money_spent
                    title = "Total Money Paid for Sessions"       


                elif y=="money":
                    for item in sessions:
                        if check!=item.connection_date:
                            ver.append(round(cost_rate(item.protocol)*0.15*item.kWh_delivered,2))
                            if check!="0":    
                                index = index + 1
                            check = item.connection_date    
                        else:
                            ver[index] = (round(ver[index] + cost_rate(item.protocol)*0.15*item.kWh_delivered, 2))
                    title = "Money Paid on Each Date"
                                    

                elif y=="total_kwh":
                    for item in sessions:
                        kwh = round(kwh + item.kWh_delivered, 2)
                        if check!= item.connection_date:
                            ver.append(kwh)
                            if check!="0":    
                                index = index + 1
                            check = item.connection_date
                        else:
                            ver[index] = kwh
                    title = "Total KWh Delivered during Sessions"            

                else:
                    for item in sessions:
                        if check!= item.connection_date:
                            ver.append(round(item.kWh_delivered,2))
                            if check!="0":    
                                index = index + 1
                            check = item.connection_date
                        else:
                            ver[index] = round(ver[index] + item.kWh_delivered,2)
                    title = "KWh Delivered on Date"                                        

            return render_template('chart.html', user = current_user, title=title, max=max(ver), labels=hor, values=ver, y=y, x=x)


    sessions = []
    date_from = datefrom[:4] + datefrom[5:7] + datefrom[8:]
    date_to = dateto[:4] + dateto[5:7] + dateto[8:]

    for i in range(len(current_user.evs)):
        pool = Session.query.filter((Session.ev_id==current_user.evs[i].id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
        sessions = sessions + pool
    sessions.sort(key=sort_criteria)

    y = 1
    money_spent = 0
    cost = []
    sesindex = []
    for x in sessions:
        sesindex.append(y)
        money_spent = round(money_spent + cost_rate(x.protocol)*0.15*x.kWh_delivered, 2)
        cost.append(money_spent)
        y = y + 1

    return render_template('chart.html', user = current_user, title="Total Money Paid", max=money_spent, labels=sesindex, values=cost, y=y, x=x)    