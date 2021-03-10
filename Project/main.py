from echarge import create_app, db, initializer
<<<<<<< HEAD

=======
>>>>>>> dff3f493bdabf268de6dd0bbcb8f2f352953952d
app = create_app()
db.app = app
initializer()

if __name__ == '__main__':
    app.run(debug=True)
    