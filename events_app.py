import sys
sys.path.insert(0, '/usr/local/rn_feeds/python/lib/python2.7/site-packages')
import flask
import json
import feedgenerator
import rn_events

app = flask.Flask(__name__)

@app.route('/')
def index():
    try:
        n = int(flask.request.args['n'])
        rn_events.fetch_hypothesis_timed()
        events = rn_events.get_events(n)
    except KeyError:
        rn_events.fetch_hypothesis_timed()
        events = rn_events.get_events()
    except ValueError:
        return flask.Response('bad value for "n"\n', 
                              status=400, 
                              mimetype='text/plain')
    data = json.dumps(events)
    return flask.Response(data, mimetype='application/json')

@app.route('/rss')
def rss():
    rn_events.fetch_hypothesis_timed()
    feed = feedgenerator.Rss201rev2Feed(
            title='ReproNim community events', 
            link='http://www.reproducibleimaging.org/events.html', 
            description='ReproNim community events.', 
            langugage='en')
    for event in reversed(rn_events.get_events()):
        feed.add_item(title=event[1], link=event[0], description=event[1])
    data = feed.writeString('utf-8')
    return flask.Response(data, mimetype='application/rss+xml')

application = app
application.debug = True

# eof
