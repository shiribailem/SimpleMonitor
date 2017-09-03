# SimpleMonitor
An extremely minimal and simple monitoring collector for servers

# Why?

I run some simple home servers and was tired of the complexity involved with big 
monitoring tools, none of them were trivial to implement.

What I wanted was an option that could just be dropped in without extensive 
dependencies and a trivial configuration requiring little to no input to get 
started.

# The Plan

The initial plan (subject to change) is to use flask and peewee to build a 
passive monitoring server with a REST api.

* Why Flask?

  Flask includes a minimal webserver component as well as the ability to use 
  uwsgi or cgi. This allows the tool to be run minimally by itself, but can be 
  scaled up later by using a traditional webserver.

* Why peewee?

  I wanted a database interface that allowed me to both use sqlite (as a 
  default) and allow the user to configure a full database server if they 
  desired.

  While I could have used sqlalchemy as I have in other projects in the past, I 
  wanted to try something simpler and found peewee. If it doesn't work out, 
  I'll probably switch to the more traditional sqlalchemy.

# How it's supposed to work

## The server itself

The plan is for the web interface to take POST or GET requests in a key/value 
format, with the value being a signed float. I will likely include a shared secret
field for minimal authentication and identification (however I do not plan to 
implement ssl natively; if security is a concern I recommend using a full
webserver).

Each of these requests the server will store in a single table containing the
timestamp of the request, the origin (identified by the secret), the key and 
the value. I plan the value to be locked to a float to allow for all common 
types of monitoring output (float can easily encompass short integers and 
booleans). Another reason for the constrained format is so that it's possible
to have a flexible single table to simplify creation of monitors.

I plan on monitor creation to be automatic at first update.

## Collecting data

The reason I'm aiming for a basic REST interface and pointedly wanting to allow
updates via GET requests is so that collectors could be as simple as curl 
requests.

Eventually I'll eventually include sample/common collectors. But I want it to 
be trivial to throw together a collector.

## Displaying data

I'm always fond of the philosophy: "Do one thing and do it well" and honestly 
don't want to expend significant effort on a display interface.

As a minimal interface, I plan to serve up a static html page at the root path 
and display data via javascript requests to the api. This page will ideally be
configurable so that users can swap it out.

I might package other tools later to provide basic extraction and/or display on
the command line.

## Notifications

Initially I do not plan on implementing notifications. However I imagine that I
will likely attach them as a step in accepting the update requests from 
collectors.

# Current Status

## Implemented

* Uses Flask (web interface and request handling), Peewee (database), and 
  PyYaml (configuration files)
* Searches for mandatory configuration files in the following order:
  - ./simplemonitor.conf
  - ~/.simplemonitor.conf
  - /etc/simplemonitor/simplemonitor.conf
* db_url config option allows passing db configuration directly to peewee
* bind_ip and bind_port can optionally be specified (defaults to "127.0.0.1" and
  9999)
* Uses secrets list in config file for minimal authentication and 
  identification. See examples directory for an example.
* Requirements can be installed with "pip install -r requirements.txt"
* Data can be inserted by making a get request to 
  http://<hostname/ip>:<port>/api/update?secret=<secret>&tag=<arbitrary string>&value=<arbitrary signed float>

## Caveats

* There's currently no built in method for viewing data. However, database is 
  not kept open when not in use, so sqlite copies can be copied and read in any 
  sqlite browser. All data is in "Monitor" table in a self-explanitory layout.
