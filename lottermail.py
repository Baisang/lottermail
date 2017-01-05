#!/usr/bin/env python3

from decimal import Decimal
from lxml import html
import os
import requests

MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY']
MAILGUN_SERVER = os.environ['MAILGUN_SERVER']
MAILGUN_ENDPOINT = "https://api.mailgun.net/v3/{}/messages".format(MAILGUN_SERVER)

# store email -> amount to notify mapping
# amount value should be an integer
# TODO: make this a database thing
emails = {}

def send_message(email, jackpot):
    jackpot = int(jackpot)
    jackpot = "$" + "{:,}".format(jackpot)
    return requests.post(
        MAILGUN_ENDPOINT,
        auth=("api", MAILGUN_API_KEY),
        data={"from": "Lottermail <postmaster@{}>".format(MAILGUN_SERVER),
              "to": email,
              "subject": "Mega Millions Jackpot " + jackpot,
              "text": "The Mega Millions Jackpot is " + jackpot + " dollars."})

def send_emails(jackpot):
    try:
        for email, amount in emails.items():
            if jackpot >= amount:
                res = send_message(email, jackpot)
                # should log res.status_code
    except Exception as e:
        print('Something went wrong during email sending.')
        print(e)

def scrape_lottery():
    try:
        page = requests.get("http://www.lotteryusa.com/mega-millions/")
        tree = html.fromstring(page.content)
        jackpot = tree.xpath('//span[@class="next-jackpot-amount"]/text()')[0]
        jackpot = Decimal(jackpot.strip('$').replace(',', ''))
        return jackpot
    except Exception as e:
        print('Something went wrong.')
        print(e)

if __name__=="__main__":
    jackpot = scrape_lottery()
    send_emails(jackpot)
