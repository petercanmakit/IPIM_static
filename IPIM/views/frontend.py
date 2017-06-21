from flask import Flask, session, request, render_template, g, redirect, Response, flash, url_for, make_response
from flask_session import Session
from jinja2 import Template

from IPIM import app
from IPIM.collision import Collision
from IPIM.main import engine

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/draw_route/', methods=['GET', 'POST'])
def draw_route():
    return render_template("draw_route.html")

# submit_route
@app.route('/submit_route/', methods=['GET', 'POST'])
def submit_route():
    # print "in submit_route"
    form = request.form
    collision = Collision(form)
    collision.syncToDBWithUid(engine)
    # print collision.cid

    # flash("Your submission is successful. Thank you very much!")
    return render_template("thanks.html")

# admin login
@app.route('/admin_login/', methods=['GET', 'POST'])
def admin_login():
    return render_template("admin_login.html")
