# Roomzilla API

This project scrapes accounts on http://www.roomzilla.net/ to create a
rudimentary JSON API.

## Getting Started

Install dependencies:

    $ pip install -r requirements.txt

Set the following environment variables:

- `ROOMZILLA_SUBDOMAIN` - The subdomain the Roomzilla account is on. If you
  access Roomzilla with http://mycoworkingspace.roomzilla.com, put
  "mycoworkingspace".
- `ROOMZILLA_PASSWORD` - The password used to access the Roomzilla account
  through HTTP Basic Authentication.

Boot 'er up:

    $ python app.py

## License

See [LICENSE](LICENSE).
