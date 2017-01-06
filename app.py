from flask import Flask, abort, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/lottermail.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    threshold = db.Column(db.Integer)

    def __init__(self, email, threshold):
        self.email = email
        self.threshold = threshold

    def __str__(self):
        return '{0} with threshold {1}'.format(self.email, self.threshold)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_email', methods=['POST'])
def add_email():
    MILLION = 1000000
    try:
        email = request.form['email']
        threshold = int(request.form['threshold']) * MILLION
        matching = User.query.filter_by(email=email).first()
        if matching:
            matching.threshold = threshold
            db.session.commit()
            return "OK updated " + str(matching)
        user = User(email, threshold)
        db.session.add(user)
        db.session.commit()
        return "OK added " + str(user)
    except Exception as e:
        print(e)

@app.route('/remove_email', methods=['GET'])
def remove_email():
    try:
        email = request.args.get('email')
        if not email:
            return "Invalid URL"
        matching = User.query.filter_by(email=email).first()
        if matching:
            db.session.delete(matching)
            db.session.commit()
            return email + " has been removed from the mailing list."
        return email + " is not on our mailing list"
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()
