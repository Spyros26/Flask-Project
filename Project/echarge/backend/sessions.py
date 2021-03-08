from flask import Blueprint, jsonify
from .auth import token_required
from ..models import Session, Point, Evehicle, Station, Operator
import json, datetime


sessions = Blueprint('sessions', __name__)

def sort_criteria(json):
    try:
        return (json.connection_date+json.connection_time)
    except KeyError:
        return 0

def nums_to_months(x):
    
    switcher = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }
    return switcher.get(x, "???")


@sessions.route('/SessionsPerPoint/<pointID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def ses_per_point(current_user, pointID, date_from, date_to):
    if current_user.role == "User":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    ses_list = []
    aa = 1
    
    point = Point.query.filter_by(point_id=pointID).first()

    station = Station.query.get(point.station_id)

    operator = Operator.query.get(station.operator_id)

    pool = Session.query.filter((Session.point_id==point.id) & (Session.connection_date>=date_from) & (Session.disconnection_date<=date_to)).all()
    pool.sort(key=sort_criteria)
    for sample in pool:
        #if int(sample.connection_date)>=int(date_from) and int(sample.disconnection_date)<=int(date_to):

        edit_start = sample.connection_date
        year_start = edit_start[:4]
        month_start = nums_to_months(edit_start[4:6])
        day_start = edit_start[6:]
        edit_fin = sample.disconnection_date
        year_fin = edit_fin[:4]
        month_fin = nums_to_months(edit_fin[4:6])
        day_fin = edit_fin[6:]

        ev = Evehicle.query.get(sample.ev_id)


        ses_list.append({'SessionIndex': aa, 'SessionID': sample.session_id, 
                        'StartedOn': year_start+" "+month_start+" "+day_start+" "+sample.connection_time,
                        'FinishedOn': year_fin+" "+month_fin+" "+day_fin+" "+sample.disconnection_time,
                        'EnergyDelivered': sample.kWh_delivered, 'Protocol': sample.protocol,
                        'Payment': sample.payment ,'VehicleType': ev.car_type})
        aa = aa + 1

    return jsonify({'Point': pointID, 'PointOperator': operator.name, 'RequestTimestamp': datetime.datetime.now(),
                    'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                    'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                    'NumberOfChargingSessions': len(ses_list), 'ChargingSessionsList:': ses_list})                        



@sessions.route('/SessionsPerStation/<stationID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def ses_per_station(current_user, stationID, date_from, date_to):
    if current_user.role == "User":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    points_list = []
    
    station = Station.query.filter_by(station_id=stationID).first()
    operator = Operator.query.get(station.operator_id)
    total_kWh_station = 0
    total_sessions = 0

    for point in station.points:
        total_kWh_point = 0
        pool = Session.query.filter((Session.point_id==point.id) & (Session.connection_date>=date_from) & (Session.disconnection_date<=date_to)).all()
        
        if len(pool) != 0:
            pool.sort(key=sort_criteria)
            for sample in pool:
                total_kWh_point = total_kWh_point + sample.kWh_delivered

            points_list.append({'PointID' : point.point_id,
                                'PointsSessions' : len(pool),
                                'EnergyDelivered' : total_kWh_point
            })
            total_kWh_station = total_kWh_station + total_kWh_point
            total_sessions = total_sessions + len(pool)
        

    return jsonify({'StationID': stationID, 'Operator': operator.name, 'RequestTimestamp': datetime.datetime.now(),
                    'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                    'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                    'TotalEnergyDelivered' : total_kWh_station,
                    'NumberofChargingSessions' : total_sessions,
                    'NumberofActivePoints' : len(points_list),
                    'SessionsSummaryList': points_list})                        
