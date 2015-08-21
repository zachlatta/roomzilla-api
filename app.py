from bs4 import BeautifulSoup
from datetime import date, time, datetime, timedelta
from flask import Flask, jsonify
import os
import re
import requests
app = Flask(__name__)

ROOMZILLA_SUBDOMAIN = os.environ['ROOMZILLA_SUBDOMAIN']
ROOMZILLA_PASSWORD = os.environ['ROOMZILLA_PASSWORD']

TIMELINE_TIME_FORMAT = '%H:%M %p'

@app.route('/')
def today():
    r = requests.get('http://' + ROOMZILLA_SUBDOMAIN + '.roomzilla.net/', auth=('', ROOMZILLA_PASSWORD))
    soup = BeautifulSoup(r.text, 'html.parser')

    rooms = []
    resp = {'rooms': rooms}

    timeline = soup.find(id='timeline')

    for tr in timeline.find('tbody').find_all('tr'):
        room = {}
        tds = tr.find_all('td')
        bookings = tds[3].find(class_='timeline')

        room['floor'] = int(tds[0].text)
        room['name'] = tds[1].text.strip()
        room['description'] = tds[1].find('a').get('title')
        room['size'] = int(tds[2].text)

        room['bookings'] = []

        for booking_div in bookings.find_all('div', {'class': 'reserved'}):
            booking = {}
            tooltip = booking_div.get('tooltip')
            id = int(booking_div.get('reservation_id'))

            # Extract the start and end time from the tooltip
            parsed_tooltip = re.match(r'(?P<title>.*) - (?P<author>.*) \((?P<start_time>.*)-(?P<end_time>.*)\)', tooltip).groupdict()

            # Create a full datetime for today from extracted start and end
            # times
            start_time = datetime.combine(datetime.today(),
                                          datetime.strptime(parsed_tooltip['start_time'], TIMELINE_TIME_FORMAT).time())
            end_time = datetime.combine(datetime.today(),
                                        datetime.strptime(parsed_tooltip['end_time'], TIMELINE_TIME_FORMAT).time())

            booking['id'] = id
            booking['title'] = parsed_tooltip['title']
            booking['author'] = parsed_tooltip['author']
            booking['start_time'] = start_time.isoformat()
            booking['end_time'] = end_time.isoformat()

            room['bookings'].append(booking)

        rooms.append(room)

    return jsonify(**resp)

if __name__ == "__main__":
    app.run(debug=True)
