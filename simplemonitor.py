#!/usr/bin/env python

from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"

@app.route('/api/update', methods=['POST', 'GET'])
def monitor_update():
    try:
        assert not request.args.get('tag') is None
        assert not request.args.get('value') is None
    except AssertionError:
        return "Error"

    tag = request.args.get('tag')
    
    try:
        value = float(request.args.get('value'))
    except ValueError:
        return "Invalid Value"

    return json.dumps({tag: value})

if __name__ == '__main__':
    app.run(debug=True)
