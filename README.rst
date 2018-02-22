ReproNim events handler.

In this directory:

- README.rst: this file
- events.DDL: events database creation code
- rn_events.py: Python module for events handling
- events_app.py: WSGI application for returning events
- mail_events: handler for events emails

Installation on virtualbrain:

- virtualenv in /usr/local/rn_feeds/python
- install rn_events.py in this virtualenv
- move events_app.py to /usr/local/rn_feeds and configure apache to serve the app
- move mail_events to /usr/local/rn_feeds and configure postfix to use this script to handle mail to events-feed
- touch /var/log/rn_events and make sure it is writable by both the apache2 user and the postfix user (e.g. chown nobody:www-data, chgrp ug+w)
- create /etc/rn_feeds.pw containing the database password
- add hypothesis users to /etc/rn_events_hypothesis
