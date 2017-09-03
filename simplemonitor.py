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

class Monitor(peewee.Model):
    #primary_id = peewee.IntegerField(primary_key=True)
    timestamp = peewee.DateTimeField(index=True, default=datetime.now)
    source = peewee.CharField(index=True, max_length=180)
    tag = peewee.CharField(index=True, max_length=180)
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

@app.route('/')
def index():
    return "Hello World!"

@app.route('/api/update', methods=['GET'])
def monitor_update():
    try:
        assert not request.args.get('tag') is None
        assert not request.args.get('value') is None
        assert not request.args.get('secret') is None
    except AssertionError:
        return "Error"

    tag = request.args.get('tag')

    if len(tag) == 0:
        return "Invalid Tag"
    
    try:
        value = float(request.args.get('value'))
    except ValueError:
        return "Invalid Value"

    secret = request.args.get('secret')

    if len(secret) == 0:
        return "Invalid Secret"

    Monitor(source=secret, tag=tag, value=value).save()

    return json.dumps({tag: value})

# Find config file

if exists("./simplemonitor.conf"):
    filename = "./simplemonitor.conf"
elif exists(expanduser("~/.simplemonitor.conf")):
    filename = expanduser("~/.simplemonitor.conf")
else:
    filename = "/etc/simplemonitor/simplemonitor.conf"

with open(filename, 'r') as config_file:
    config = yaml.load(config_file.read())

database_proxy.initialize(dbconnect(config['db_url']))
database_proxy.connect()
database_proxy.create_tables([Monitor], safe=True)

if __name__ == '__main__':
    app.run(debug=True)
