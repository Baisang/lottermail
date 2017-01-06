# lottermail
Service to sign up for lottery-related emails

Let's say you only want to play Mega Millions when the jackpot is over $50 million. But how would you know when that happens?
Checking websites every day is annoying and a waste of time. Instead, subscribe to `lottermail`, where you can get email notifications
when the Mega Millions jackpot is over your specified amount.

lottermail is powered by `python3`, `flask`, and temporarily `sqlite3`. We also use `celery` to schedule periodic emails, 
with `rabbitmq` as our message broker. No backend yet but it'll probably be `redis`. We use free Mailgun to send emails.

## Why didn't you just use `cron`??
Because that would be boring

## Installation
Want to host your own lottermail? Thanks to open source licenses, you can! Get started with the usual:

1. Clone this repo `git clone https://github.com/Baisang/lottermail.git`
2. Make a `virtualenv` and `pip3 install -r requirements.txt`

You'll also need to have `celery` and `rabbitmq` (or any other message broker) installed and running. Have fun! Be sure to change
the config values in `app.py` and then

3. Get Mailgun API credentials
4. Set environment variables for your Mailgun API key and the free server they give you (look at `app.py`)
5. Start up everything, the flask app, rabbitmq, celery beat and celery worker. You can be lazy like me and just do the worker
and beat at the same time if you want, but don't do it in real life.
6. If you win the lottery from this website please give me like $5 I'd really appreciate it
