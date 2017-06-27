import os

from flask import Flask, session, request, render_template, g, redirect, Response, flash, url_for, make_response
from flask_session import Session
from jinja2 import Template

from database import dbConnect

from collision import Collision

# DATABASEURI = "postgresql://peter:940611@127.0.0.1/geo" # mac
DATABASEURI = "postgresql://ipim:admin_ipim@127.0.0.1/ipim" # gg cloud linux vm
engine = dbConnect(DATABASEURI)

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'Jiajun_is_the_best'


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass
