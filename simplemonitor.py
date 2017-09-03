#!/usr/bin/env python

from flask import Flask, request
import peewee
from playhouse.db_url import connect as dbconnect
from datetime import datetime
from os.path import expanduser, exists
import json
import yaml

# Peewee Code

# Use a proxy so that database can be selected in configuration.
database_proxy = peewee.Proxy()

# Make empty config to avoid any out-of-order reference confusion
config = {}

class Monitor(peewee.Model):
    # Timestamp is automatically set at the time the entry is created.
    timestamp = peewee.DateTimeField(index=True, default=datetime.now)
    # I set 180 because I misremembered the twitter length of 140.
    # Should be more than enough for the name of a server or a sensor.
    source = peewee.CharField(index=True, max_length=180)
    tag = peewee.CharField(index=True, max_length=180)
    # All values are in signed float as that should easily hold the majority of
    # monitoring data types: small integers, boolean, percentage
    value = peewee.FloatField(index=True)
    
    class Meta:
        database = database_proxy

# Flask Code

app = Flask(__name__)

# Connect and disconnect peewee database for each request.
@app.before_request
def _db_connect():
    database_proxy.connect()

@app.teardown_request
def _db_close(exc):
    if not database_proxy.is_closed():
        database_proxy.close()

# Placeholder. Later will use configurable static html file.
@app.route('/')
def index():
    return "Hello World!"

# The primary workhorse. This is how data gets loaded in.
@app.route('/api/update', methods=['GET'])
def monitor_update():

    # Let's make sure that the required values exist.
    try:
        assert not request.args.get('tag') is None
        assert not request.args.get('value') is None
        assert not request.args.get('secret') is None
    except AssertionError:
        # Sloppy placeholder output so there's at least some clue what went 
        # wrong.
        return "Error\n"

    # Get tag and make sure that it is longer than 0
    tag = request.args.get('tag')

    if len(tag) == 0:
        return "Invalid Tag\n"
    
    # Get value and make sure that it's a float
    try:
        value = float(request.args.get('value'))
    except ValueError:
        return "Invalid Value\n"

    # Get secret, making sure it exists in config
    secret = request.args.get('secret')

    if len(secret) == 0 or not secret in config['secrets'].keys():
        return "Invalid Secret\n"

    # Map secret to the hostname
    source = config['secrets'][secret]

    # Create database entry.
    Monitor(source=source, tag=tag, value=value).save()

    # Spit out some data to confirm that it was received properly
    return json.dumps({tag: value}) + '\n'

# Find config file

if exists("./simplemonitor.conf"):
    filename = "./simplemonitor.conf"
elif exists(expanduser("~/.simplemonitor.conf")):
    filename = expanduser("~/.simplemonitor.conf")
elif exists("/etc/simplemonitor/simplemonitor.conf"):
    filename = "/etc/simplemonitor/simplemonitor.conf"
else:
    print("No configuration file found!")
    exit(1)

# Load config file
# TODO: validate config file

with open(filename, 'r') as config_file:
    config = yaml.load(config_file.read())

# Connect to database given in config

database_proxy.initialize(dbconnect(config['db_url']))
database_proxy.connect()

# Make sure tables exist
database_proxy.create_tables([Monitor], safe=True)

database_proxy.close()

# If run directly, load bind values, debug, and launch flask.
if __name__ == '__main__':
    if not "bind_ip" in config.keys():
        ip = "127.0.0.1"
    else:
        ip = config["bind_ip"]

    if not "bind_port" in config.keys():
        port = 9999
    else:
        port = int(config["bind_port"])

    if "debug" in config.keys():
        debug = config["debug"]
    else:
        debug = False

    app.run(debug=debug, host=ip, port=port)
