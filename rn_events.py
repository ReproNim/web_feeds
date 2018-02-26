import os
import time
import datetime
import psycopg2
import h_annot

db_params = {'host': 'localhost', 
             'dbname': 'rn_events', 
             'user': 'rn_feeds', 
             'password': open('/etc/rn_feeds.pw').read().strip()}

# minimum time in seconds between hypothesis updates
hypothesis_dt = 600
hypothesis_t_fname = '/tmp/rn_events_t'

try:
    with open('/etc/rn_events_hypothesis') as fo:
        allowed_hypothesis_users = [ line.strip().lower() for line in fo ]
except IOError:
    allowed_hypothesis_users = []

def log(msg):
    with open('/var/log/rn_events', 'a') as fo:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for line in msg.rstrip('\n').split('\n'):
            fo.write('%s [%5d]  %s\n' % (now, os.getpid(), line))
    return

def get_config(name):
    """get_config(name) -> value

    gets a configuration value from the database

    raises KeyError if the name is not found
    """
    with psycopg2.connect(**db_params) as db:
        with db.cursor() as c:
            c.execute("SELECT value FROM config WHERE name = %s", (name, ))
            if c.rowcount == 0:
                raise KeyError(name)
            value = c.fetchone()[0]
    return value

def set_config(name, value):
    """set_config(name, value) -> None

    sets or updates a configuration value in the database
    """
    with psycopg2.connect(**db_params) as db:
        with db.cursor() as c:
            select_query = "SELECT * FROM config WHERE name = %s FOR UPDATE"
            c.execute(select_query, (name, ))
            if c.rowcount == 0:
                query = "INSERT INTO config (name, value) VALUES (%s, %s)"
                params = (name, value)
            else:
                query = "UPDATE config SET value = %s WHERE name = %s"
                params = (value, name)
            c.execute(query, params)
    return

def get_events(n=None):
    """get_events([n]) -> list of events

    events are (url, headline) tuples sorted by event update date (descending)

    set n to get the n latest events
    """
    if n is None:
        query = """SELECT url, headline 
                     FROM event 
                    WHERE active 
                    ORDER BY time DESC"""
        params = ()
    elif isinstance(n, int):
        query = """SELECT url, headline 
                     FROM event 
                    WHERE active 
                    ORDER BY time DESC 
                    LIMIT %s"""
        params = (n, )
    else:
        raise TypeError('n must be an integer or None')
    with psycopg2.connect(**db_params) as db:
        with db.cursor() as c:
            c.execute(query, params)
            events = list(c)
    return events

def add_email_event(address, url, headline):
    """add_email_event(address, url, headline) -> None"""
    address = address.lower()
    query = """INSERT INTO event (source, source_user, url, headline)
                VALUES (%s, %s, %s, %s)"""
    params = ('email', address, url, headline)
    with psycopg2.connect(**db_params) as db:
        with db.cursor() as c:
            c.execute(query, params)
    return

def add_or_update_hypothesis_event(user, annot_id, url, headline, updated):
    """add_or_update_hypothesis_event(user, annot_id, url, headline) -> None

    create an event, or if a (hypothesis-generated) event with the given 
    hypothesis ID exists, update that event
    """
    user = user.lower()
    annot_id = str(annot_id)
    select_query = """SELECT id, time 
                        FROM event 
                       WHERE source = %s 
                         AND source_id = %s 
                         FOR UPDATE"""
    select_params = ('hypothesis', annot_id)
    insert_query = """INSERT INTO event (time, 
                                         source, 
                                         source_user, 
                                         source_id, 
                                         url, 
                                         headline) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
    insert_params = (updated, 'hypothesis', user, annot_id, url, headline)
    update_query = """UPDATE event 
                         SET time = %s, url = %s, headline = %s 
                       WHERE id = %s"""
    with psycopg2.connect(**db_params) as db:
        with db.cursor() as c:
            c.execute(select_query, select_params)
            if c.rowcount == 0:
                c.execute(insert_query, insert_params)
            else:
                row = c.fetchone()
                if row[1] < updated:
                    event_id = row[0]
                    update_params = (updated, url, headline, event_id)
                    c.execute(update_query, update_params)
                else:
                    # we have the event and it's up to date
                    pass
    return

def fetch_hypothesis():
    """fetch_hypothesis() -> None

    fetch hypothesis annotations and update the events database
    """
    for annotation in h_annot.Annotation.search(sort='updated', 
                                                tag='repronim:event'):
        user = annotation.user
        if user.startswith('acct:'):
            user = user[5:]
        if user.endswith('@hypothes.is'):
            user = user[:-12]
        add_or_update_hypothesis_event(user, 
                                       annotation.id, 
                                       annotation.uri, 
                                       annotation.text, 
                                       annotation.updated)
    return

def fetch_hypothesis_timed():
    """fetch_hypothesis_timed() -> None

    fetch hypothesis annotations and update the events database, 
    but no more than once every hypothesis_dt
    """
    update_flag = False
    try:
        so = os.stat(hypothesis_t_fname)
        if time.time() - so.st_mtime > hypothesis_dt:
            update_flag = True
    except OSError:
        open(hypothesis_t_fname, 'w')
        update_flag = True
    if not update_flag:
        return
    fetch_hypothesis()
    os.utime(hypothesis_t_fname, None)
    return

# eof
