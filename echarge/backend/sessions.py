from flask import Blueprint, jsonify, request, make_response
from .auth import token_required
from ..models import Session, Point, Evehicle, Station, Operator, Energyprovider
import json, datetime
import pandas as pd
import flask_csv as fcsv


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
        return make_response('Not allowed to perform this action!', 401)

    askformat = request.args.get('format', default='json', type=str)
    if askformat!='json' and askformat!='csv':
        return make_response('Cannot accept format. Supported formats are json (default) and csv.', 400)

    ses_list = []

    objl = []
    indexl = []
    sessionl = []
    startl = []
    finishl = []
    energyl = []
    protocoll = []
    paymentl = []
    vehiclel = []

    aa = 1
    timestamp = datetime.datetime.now()

    point = Point.query.filter_by(point_id=pointID).first()

    station = Station.query.get(point.station_id)

    operator = Operator.query.get(station.operator_id)

    pool = Session.query.filter((Session.point_id==point.id) & (Session.connection_date>=date_from) & (Session.done_date<=date_to)).all()
    pool.sort(key=sort_criteria)
    for sample in pool:
        started_on = sample.connection_date[:4] + "-" + sample.connection_date[4:6] + "-" + sample.connection_date[6:] + "  " + sample.connection_time[:2] + ":" + sample.connection_time[2:4] + ":" + sample.connection_time[4:]
        done_on = sample.done_date[:4] + "-" + sample.done_date[4:6] + "-" + sample.done_date[6:] + "  " + sample.done_time[:2] + ":" + sample.done_time[2:4] + ":" + sample.done_time[4:]

        ev = Evehicle.query.get(sample.ev_id)

        if askformat=='json':
            ses_list.append({'SessionIndex': aa, 'SessionID': sample.session_id, 
                            'StartedOn': started_on,
                            'FinishedOn': done_on,
                            'EnergyDelivered': sample.kWh_delivered, 'Protocol': sample.protocol,
                            'Payment': sample.payment ,'VehicleType': ev.car_type})
        else:
            indexl.append(aa)
            sessionl.append(sample.session_id)
            startl.append(started_on)
            finishl.append(done_on)
            energyl.append(sample.kWh_delivered)
            protocoll.append(sample.protocol)
            paymentl.append(sample.payment)
            vehiclel.append(ev.car_type)
        
        aa = aa + 1

    if askformat=='json':
        return jsonify({'Point': pointID, 'PointOperator': operator.name, 'RequestTimestamp': timestamp,
                        'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                        'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                        'NumberOfChargingSessions': len(ses_list), 'ChargingSessionsList:': ses_list})                        

    else:
        for x in range(0,len(pool)):
            objl.append({'Point': pointID, 'PointOperator': operator.name, 'RequestTimestamp': timestamp,
                        'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                        'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:], 
                        'NumberOfChargingSessions': len(indexl),
                        'SessionIndex': indexl[x], 'SessionID': sessionl[x], 'StartedOn': startl[x],
                        'FinishedOn': finishl[x], 'EnergyDelivered': energyl[x], 'Protocol': protocoll[x],
                        'Payment': paymentl[x] ,'VehicleType': vehiclel[x]})

        return fcsv.send_csv(objl, "reply.csv", ["Point", "PointOperator", "RequestTimestamp",
                                                "PeriodFrom", "PeriodTo", "NumberOfChargingSessions",
                                                "SessionIndex", "SessionID", "StartedOn", "FinishedOn",
                                                "EnergyDelivered", "Protocol", "Payment", "VehicleType"], delimiter=';')                



@sessions.route('/SessionsPerStation/<stationID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def ses_per_station(current_user, stationID, date_from, date_to):
    if current_user.role == "User":
        return make_response('Not allowed to perform this action!', 401)

    askformat = request.args.get('format', default='json', type=str)
    if askformat!='json' and askformat!='csv':
        return make_response('Cannot accept format. Supported formats are json (default) and csv.', 400)

    points_list = []
    
    objl = []
    pointidl = []
    pointsessionsl = []
    energyl = []

    timestamp = datetime.datetime.now()

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

            if askformat=='json':
                points_list.append({'PointID' : point.point_id,
                                    'PointsSessions' : len(pool),
                                    'EnergyDelivered' : total_kWh_point
                })

            else:
                pointidl.append(point.point_id)
                pointsessionsl.append(len(pool))
                energyl.append(total_kWh_point)   

            total_kWh_station = total_kWh_station + total_kWh_point
            total_sessions = total_sessions + len(pool)

    if askformat=='json':
        return jsonify({'StationID': stationID, 'Operator': operator.name, 'RequestTimestamp': timestamp,
                        'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                        'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                        'TotalEnergyDelivered' : total_kWh_station,
                        'NumberOfChargingSessions' : total_sessions,
                        'NumberOfActivePoints' : len(points_list),
                        'SessionsSummaryList': points_list})

    else:
        for x in range(0,len(pointidl)):
            objl.append({'StationID': stationID, 'Operator': operator.name, 'RequestTimestamp': timestamp,
                        'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                        'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                        'TotalEnergyDelivered' : total_kWh_station,
                        'NumberOfChargingSessions' : total_sessions,
                        'NumberOfActivePoints' : len(pointidl), 'PointID' : pointidl[x],
                        'PointsSessions' : pointsessionsl[x], 'EnergyDelivered' : energyl[x]})

        return fcsv.send_csv(objl, "reply.csv", ["StationID", "Operator", "RequestTimestamp",
                                                "PeriodFrom", "PeriodTo", "TotalEnergyDelivered",
                                                "NumberOfChargingSessions", "NumberOfActivePoints",
                                                "PointID", "PointSessions", "EnergyDelivered"], delimiter=';')                             


@sessions.route('/SessionsPerEV/<vehicleID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def ses_per_ev(current_user, vehicleID, date_from, date_to):
    if current_user.role == "User":
        return make_response('Not allowed to perform this action!', 401)

    askformat = request.args.get('format', default='json', type=str)
    if askformat!='json' and askformat!='csv':
        return make_response('Cannot accept format. Supported formats are json (default) and csv.', 400)

    ses_list = []
    
    objl = []
    indexl = []
    sessionl = []
    providerl = []
    startl = []
    finishl = []
    energyl = []
    pprl = []
    kwhcost = []
    sesscostl = []

    ev = Evehicle.query.filter_by(car_id=vehicleID).first()
    
    timestamp = datetime.datetime.now()
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

        if askformat=='json':
            ses_list.append({'SessionIndex': aa, 'SessionID': sample.session_id,
                        'EnergyProvider' : provider.name, 
                        'StartedOn': started_on,
                        'FinishedOn': done_on,
                        'EnergyDelivered': sample.kWh_delivered, 'PricePolicyRef': "Standard Pricing based on KWh delivered and Session Protocol. " + 
                        "e.g: Session cost = cost_rate*kWh_delivered*costPerKWh " + "where cost_rate = 1 (Session Protocol = Level 1: Low) / cost_rate = 2 (Session Protocol = Level 2: Medium) / cost_rate = 3 (Session Protocol = Level 3: High)",
                        'CostPerKWh': costPerKWh ,'SessionCost': round(cost_rate*costPerKWh*sample.kWh_delivered, 2)})

        else:
            indexl.append(aa)
            sessionl.append(sample.session_id)
            providerl.append(provider.name)
            startl.append(started_on)
            finishl.append(done_on)
            energyl.append(sample.kWh_delivered)
            pprl.append("Standard Pricing based on KWh delivered and Session Protocol. " + 
                        "e.g: Session cost = cost_rate*kWh_delivered*costPerKWh " + 
                        "where cost_rate = 1 (Session Protocol = Level 1: Low) / cost_rate = 2 (Session Protocol = Level 2: Medium) / cost_rate = 3 (Session Protocol = Level 3: High)")
            kwhcost.append(costPerKWh)
            sesscostl.append(round(cost_rate*costPerKWh*sample.kWh_delivered, 2))

        aa = aa + 1

    if askformat=='json':
        return jsonify({'VehicleID': vehicleID, 'RequestTimestamp': timestamp,
                        'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                        'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                        'TotalEnergyConsumed' : total_kWh,
                        'NumberOfVisitedPoints' : len(visited_points),
                        'NumberOfVehicleChargingSessions' : len(ses_list),
                        'VehicleChargingSessionsList': ses_list})                        

    else:
        for x in range(0,len(pool)):
            objl.append({'VehicleID': vehicleID, 'RequestTimestamp': timestamp,
                        'PeriodFrom': date_from[:4]+" "+nums_to_months(date_from[4:6])+" "+date_from[6:],
                        'PeriodTo': date_to[:4]+" "+nums_to_months(date_to[4:6])+" "+date_to[6:],
                        'TotalEnergyConsumed' : total_kWh, 'NumberOfVisitedPoints' : len(visited_points),
                        'NumberOfVehicleChargingSessions' : len(pool), 'SessionIndex': indexl[x], 
                        'SessionID': sessionl[x], 'EnergyProvider' : providerl[x], 
                        'StartedOn': startl[x], 'FinishedOn': finishl[x],
                        'EnergyDelivered': energyl[x], 'PricePolicyRef': pprl[x], 
                        'CostPerKWh': kwhcost[x] ,'SessionCost': round(sesscostl[x],2)})

        return fcsv.send_csv(objl, "reply.csv", ["VehicleID", "RequestTimestamp",
                                                "PeriodFrom", "PeriodTo", "TotalEnergyConsumed",
                                                "NumberOfVisitedPoints", "NumberOfVehicleChargingSessions",
                                                "SessionIndex", "SessionID", "EnergyProvider", 
                                                "StartedOn", "FinishedOn", "EnergyDelivered", 
                                                "PricePolicyRef", "CostPerKWh", "SessionCost"], delimiter=';')                


@sessions.route('/SessionsPerProvider/<providerID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def ses_per_provider(current_user, providerID, date_from, date_to):
    if current_user.role == "User":
        return make_response('Not allowed to perform this action!', 401)

    askformat = request.args.get('format', default='json', type=str)
    if askformat!='json' and askformat!='csv':
        return make_response('Cannot accept format. Supported formats are json (default) and csv.', 400)

    sess_list = []
    costPerKWh = 0.15
    poolall = []

    objl = []
    stationidl = []
    sessionidl = []
    vehicleidl = []
    startl = []
    finishl = []
    energyl = []
    pprl = []
    kwhcostl = []
    totalcostl = []

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
        
        if askformat=='json':
            sess_list.append({  'StationID': station.station_id,
                                'SessionID': sample.session_id, 'VehicleID': ev.car_id, 'StartedOn': started_on,
                                'FinishedOn': done_on, 'EnergyDelivered': sample.kWh_delivered, 
                                'PricePolicyRef': "Standard Pricing based on KWh delivered and Session Protocol. " + 
                                "e.g: Session cost = cost_rate*kWh_delivered*costPerKWh " + "where cost_rate = 1 (Session Protocol = Level 1: Low) / cost_rate = 2 (Session Protocol = Level 2: Medium) / cost_rate = 3 (Session Protocol = Level 3: High)",
                                'CostPerKWh': costPerKWh,
                                'TotalCost': round(cost_rate*costPerKWh*sample.kWh_delivered, 2)})

        else:
            stationidl.append(station.station_id)
            sessionidl.append(sample.session_id)
            vehicleidl.append(ev.car_id)
            startl.append(started_on)
            finishl.append(done_on)
            energyl.append(sample.kWh_delivered)
            pprl.append("Standard Pricing based on KWh delivered and Session Protocol. " + 
                        "e.g: Session cost = cost_rate*kWh_delivered*costPerKWh " + 
                        "where cost_rate = 1 (Session Protocol = Level 1: Low) / cost_rate = 2 (Session Protocol = Level 2: Medium) / cost_rate = 3 (Session Protocol = Level 3: High)")
            kwhcostl.append(costPerKWh)
            totalcostl.append(round(cost_rate*costPerKWh*sample.kWh_delivered, 2))

    if askformat=='json':
        return jsonify({'ProviderID': providerID, 'ProviderName': provider.name, 'ProviderChargingSessionsList': sess_list})                            

    else:
        for x in range(0,len(poolall)):
            objl.append({'ProviderID': providerID, 'ProviderName': provider.name,
                        'StationID': stationidl[x],
                        'SessionID': sessionidl[x], 'VehicleID': vehicleidl[x], 'StartedOn': startl[x],
                        'FinishedOn': finishl[x], 'EnergyDelivered': energyl[x], 
                        'PricePolicyRef': pprl[x], 'CostPerKWh': kwhcostl[x],
                        'TotalCost': round(totalcostl[x], 2)})

        return fcsv.send_csv(objl, "reply.csv", ["ProviderID", "ProviderName", "StationID",
                                                "SessionID", "VehicleID", "StartedOn",
                                                "FinishedOn", "EnergyDelivered",
                                                "PricePolicyRef", "CostPerKWh", "TotalCost"], delimiter=';')  