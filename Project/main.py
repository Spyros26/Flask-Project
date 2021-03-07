from echarge import create_app, default_admin, default_evs, default_operators, default_points_stations, default_users , default_sessions ,db

app = create_app()
db.app = app
default_admin('admin','petrol4ever')
#default_operators('echarge/Operators_data.csv')
default_points_stations('echarge/points.csv')
default_users()
default_evs('echarge/electric_vehicles_data.json')
default_sessions('echarge/caltech_acndata_sessions_12month.json')

if __name__ == '__main__':
    app.run(debug=True)
    