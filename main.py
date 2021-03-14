from echarge import create_app, db, initializer
app = create_app()
db.app = app
initializer()

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(debug=True, ssl_context=('echarge/certificates/cert.prem','echarge/certificates/key.prem' ))