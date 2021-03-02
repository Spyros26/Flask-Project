from echarge import create_app, default_admin, default_evs, db

app = create_app()
db.app = app
default_admin('admin','petrol4ever')
#default_evs('website/static/test.json')
default_evs('echarge/electric_vehicles_data.json')

if __name__ == '__main__':
    app.run(debug=True)
    