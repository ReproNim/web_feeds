import sys
sys.path.insert(0, '/usr/local/rn_feeds/python/lib/python2.7/site-packages')
import flask
import json
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

application = app
application.debug = True

# eof
