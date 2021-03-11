from flask import Blueprint, jsonify
from .auth import token_required
from ..models import Session, Point, Evehicle, Station, Operator, Energyprovider
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

    pool = Session.query.filter((Session.point_id==point.id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
    pool.sort(key=sort_criteria)
    for sample in pool:
        #if int(sample.connection_date)>=int(date_from) and int(sample.disconnection_date)<=int(date_to):
   
        started_on = sample.connection_date[:4] + "-" + sample.connection_date[4:6] + "-" + sample.connection_date[6:] + "  " + sample.connection_time[:2] + ":" + sample.connection_time[2:4] + ":" + sample.connection_time[4:]
        done_on = sample.done_date[:4] + "-" + sample.done_date[4:6] + "-" + sample.done_date[6:] + "  " + sample.done_time[:2] + ":" + sample.done_time[2:4] + ":" + sample.done_time[4:]

        ev = Evehicle.query.get(sample.ev_id)


        ses_list.append({'SessionIndex': aa, 'SessionID': sample.session_id, 
                        'StartedOn': started_on,
                        'FinishedOn': done_on,
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
        pool = Session.query.filter((Session.point_id==point.id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
        
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
                    'NumberOfChargingSessions' : total_sessions,
                    'NumberOfActivePoints' : len(points_list),
                    'SessionsSummaryList': points_list})            


@sessions.route('/SessionsPerEV/<vehicleID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def ses_per_ev(current_user, vehicleID, date_from, date_to):
    if current_user.role == "User":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    ses_list = []
    
    ev = Evehicle.query.filter_by(car_id=vehicleID).first()
    
    total_kWh = 0
    costPerKWh = 0.15
    aa = 1
    visited_points = []

    pool = Session.query.filter((Session.ev_id==ev.id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
    pool.sort(key=sort_criteria)
        
    for sample in pool:
        point = Point.query.get(sample.point_id)
        station = Station.query.get(point.station_id)
        provider = Energyprovider.query.get(station.provider_id)

        total_kWh = total_kWh + sample.kWh_delivered
        if sample.point_id not in visited_points:
            visited_points.append(sample.point_id)
    
        started_on = sample.connection_date[:4] + "-" + sample.connection_date[4:6] + "-" + sample.connection_date[6:] + "  " + sample.connection_time[:2] + ":" + sample.connection_time[2:4] + ":" + sample.connection_time[4:]
        done_on = sample.done_date[:4] + "-" + sample.done_date[4:6] + "-" + sample.done_date[6:] + "  " + sample.done_time[:2] + ":" + sample.done_time[2:4] + ":" + sample.done_time[4:]

        if sample.protocol == "Level 1: Low":
                cost_rate = 1
        elif sample.protocol == "Level 2: Medium":
                cost_rate = 2
        elif sample.protocol == "Level 3: High":
                cost_rate = 3

        ses_list.append({'SessionIndex': aa, 'SessionID': sample.session_id,
                    'EnergyProvider' : provider.name, 
                    'StartedOn': started_on,
                    'FinishedOn': done_on,
                    'EnergyDelivered': sample.kWh_delivered, 'PricePolicyRef': "Standard Pricing based on KWh delivered and Session Protocol. " + 
                    "e.g: Session cost = cost_rate*kWh_delivered*costPerKWh " + "where cost_rate = 1 (Session Protocol = Level 1: Low) / cost_rate = 2 (Session Protocol = Level 2: Medium) / cost_rate = 3 (Session Protocol = Level 3: High)",
                    'CostPerKWh': costPerKWh ,'SessionCost': cost_rate*costPerKWh*sample.kWh_delivered})
            
        aa = aa + 1

    return jsonify({'VehicleID': vehicleID, 'RequestTimestamp': datetime.datetime.now(),
                    'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                    'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                    'TotalEnergyConsumed' : total_kWh,
                    'NumberOfVisitedPoints' : len(visited_points),
                    'NumberOfVehicleChargingSessions' : len(ses_list),
                    'VehicleChargingSessionsList': ses_list})                        


@sessions.route('/SessionsPerProvider/<providerID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def ses_per_provider(current_user, providerID, date_from, date_to):
    if current_user.role == "User":
        return jsonify({'message' : 'Not allowed to perform this action!'})

    sess_list = []
    costPerKWh = 0.15
    poolall = []

    provider = Energyprovider.query.filter_by(provider_id=providerID).first()

    for station in provider.stations:
        for point in station.points:
            pool = Session.query.filter((Session.point_id==point.id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
            poolall = poolall + pool
    
    poolall.sort(key=sort_criteria)
    for sample in poolall:
        point = Point.query.filter_by(id=sample.point_id).first()
        station = Station.query.filter_by(id=point.station_id).first()
        ev = Evehicle.query.filter_by(id=sample.ev_id).first()

        if sample.protocol == "Level 1: Low":
                cost_rate = 1
        elif sample.protocol == "Level 2: Medium":
                cost_rate = 2
        elif sample.protocol == "Level 3: High":
                cost_rate = 3

        started_on = sample.connection_date[:4] + "-" + sample.connection_date[4:6] + "-" + sample.connection_date[6:] + "  " + sample.connection_time[:2] + ":" + sample.connection_time[2:4] + ":" + sample.connection_time[4:]
        done_on = sample.done_date[:4] + "-" + sample.done_date[4:6] + "-" + sample.done_date[6:] + "  " + sample.done_time[:2] + ":" + sample.done_time[2:4] + ":" + sample.done_time[4:]
        sess_list.append({  'StationID': station.station_id,
                            'SessionID': sample.session_id, 'VehicleID': ev.car_id, 'StartedOn': started_on,
                            'FinishedOn': done_on, 'EnergyDelivered': sample.kWh_delivered, 
                            'PricePolicyRef': "Standard Pricing based on KWh delivered and Session Protocol. " + 
                            "e.g: Session cost = cost_rate*kWh_delivered*costPerKWh " + "where cost_rate = 1 (Session Protocol = Level 1: Low) / cost_rate = 2 (Session Protocol = Level 2: Medium) / cost_rate = 3 (Session Protocol = Level 3: High)",
                            'CostPerKWh': costPerKWh,
                            'TotalCost': cost_rate*costPerKWh*sample.kWh_delivered})

    return jsonify({'ProviderID': providerID, 'ProviderName': provider.name, 'ProviderChargingSessionsList': sess_list})                            