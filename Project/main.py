from echarge import create_app, db, initializer

app = create_app()
db.app = app
initializer()

if __name__ == '__main__':
    app.run(debug=True)
    