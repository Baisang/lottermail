#!/usr/bin/env python3

from lxml import html
import os
import requests

MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY']
MAILGUN_SERVER = os.environ['MAILGUN_SERVER']
MAILGUN_ENDPOINT = "https://api.mailgun.net/v3/{}/messages".format(MAILGUN_SERVER)

def send_message(email, jackpot):
    jackpot = "$" + "{:,}".format(jackpot)
    return requests.post(
        MAILGUN_ENDPOINT,
        auth=("api", MAILGUN_API_KEY),
        data={"from": "Lottermail <postmaster@{}>".format(MAILGUN_SERVER),
              "to": email,
              "subject": "Today's Mega Millions Jackpot: " + jackpot,
              "text": "The Mega Millions Jackpot is " + jackpot + " dollars."})

def scrape_lottery():
    try:
        page = requests.get("http://www.lotteryusa.com/mega-millions/")
        tree = html.fromstring(page.content)
        jackpot = tree.xpath('//span[@class="next-jackpot-amount"]/text()')[0]
        jackpot = int(jackpot.strip('$').replace(',', ''))
        return jackpot
    except Exception as e:
        print('Something went wrong.')
        print(e)
        return -1
