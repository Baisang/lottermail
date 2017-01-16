from celery import Celery
from celery.schedules import crontab
from flask import Flask, abort, render_template, request
from flask_sqlalchemy import SQLAlchemy
from lottermail import send_message, scrape_lottery
import os

### Configs
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/lottermail.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = 'amqp://myuser:mypassword@127.0.1.1/myvhost'
db = SQLAlchemy(app)

### Celery
def make_celery(app):
    # TODO: add a backend like redis/move from using rabbitmq to redis as broker
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celeryapp = make_celery(app)
celeryapp.conf.timezone = "America/Los_Angeles"
celeryapp.conf.beat_schedule = {
    # Execute every day at 6:30am PST
    'email-every-morning': {
        'task': 'app.email',
        'schedule': crontab(hour=12+9, minute=43)
    }
}

@celeryapp.task(name='app.email')
def email():
    jackpot = scrape_lottery()
    if jackpot > 0:
        db = SQLAlchemy(app)
        for user in User.query.all():
            if jackpot >= user.threshold:
                send_email.apply_async(args=[user.email, jackpot])

@celeryapp.task(name='app.send_email')
def send_email(email, jackpot):
    try:
        res = send_message(email, jackpot)
        print(res)
    except Exception as e:
        print(e)

### Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    threshold = db.Column(db.Integer)

    def __init__(self, email, threshold):
        self.email = email
        self.threshold = threshold

    def __str__(self):
        return '{0} with threshold {1}'.format(self.email, self.threshold)

### Endpoints
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
    app.run('0.0.0.0')
