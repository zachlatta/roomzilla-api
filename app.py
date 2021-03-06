from bs4 import BeautifulSoup
from datetime import date, time, datetime, timedelta
from flask import Flask, jsonify, request
import os
import re
import requests
app = Flask(__name__)

ROOMZILLA_SUBDOMAIN = os.environ['ROOMZILLA_SUBDOMAIN']
ROOMZILLA_PASSWORD = os.environ['ROOMZILLA_PASSWORD']

TIMELINE_TIME_FORMAT = '%H:%M %p'

def parse_bookings(booking_list):
    bookings = []

    for booking_div in booking_list.find_all('div', {'class': 'reserved'}):
        booking = {}
        tooltip = booking_div.get('tooltip')
        id = int(booking_div.get('reservation_id'))

        # Extract the start and end time from the tooltip
        parsed_tooltip = re.match(r'(?P<purpose>.*) - (?P<host>.*) \((?P<start_time>.*)-(?P<end_time>.*)\)', tooltip).groupdict()

        # Create a full datetime for today from extracted start and end
        # times
        start_time = datetime.combine(datetime.today(),
                                        datetime.strptime(parsed_tooltip['start_time'], TIMELINE_TIME_FORMAT).time())
        end_time = datetime.combine(datetime.today(),
                                    datetime.strptime(parsed_tooltip['end_time'], TIMELINE_TIME_FORMAT).time())

        booking['id'] = id
        booking['purpose'] = parsed_tooltip['purpose']
        booking['host'] = parsed_tooltip['host']
        booking['start_time'] = start_time.isoformat()
        booking['end_time'] = end_time.isoformat()

        bookings.append(booking)

    return bookings

def parse_rooms(page):
    rooms = []
    timeline = page.find(id='timeline')

    for tr in timeline.find('tbody').find_all('tr'):
        room = {}
        tds = tr.find_all('td')
        bookings = tds[3].find(class_='timeline')

        room['id'] = bookings.find('div').get('room_keyname')
        room['floor'] = int(tds[0].text)
        room['name'] = tds[1].text.strip()
        room['description'] = tds[1].find('a').get('title')
        room['size'] = int(tds[2].text)
        room['bookings'] = parse_bookings(bookings)

        rooms.append(room)

    return rooms

@app.route('/rooms')
@app.route('/rooms/<room>')
def get_room(room=None):
    day = request.args.get('day', date.today().isoformat())

    path = '/rooms/{}'.format(room) if room else '/rooms'
    url = 'http://{}.roomzilla.net{}?day={}'.format(ROOMZILLA_SUBDOMAIN, path, day)

    r = requests.get(url, auth=('', ROOMZILLA_PASSWORD))
    soup = BeautifulSoup(r.text, 'html.parser')

    resp = {
        'date': day,
        'rooms': parse_rooms(soup),
    }

    return jsonify(**resp)

@app.route('/ping')
def ping():
    return 'Pong!'

if __name__ == "__main__":
    app.run(debug=True)
