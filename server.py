#!/usr/bin/env python2.7

"""

To run locally

    python server.py

Go to http://localhost:8111 in your browser

"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from flask import Flask, session, request, render_template, g, redirect, Response, flash, url_for, make_response
from flask_session import Session
from jinja2 import Template

import datetime
import time

class Collision(object):
    __tablename__ = 'collisions'

    cid = long(-1)

    acc_date = None

    state = ""
    city = ""
    street = ""
    cross_street = ""

    cartype = ""
    time_of_day = ""
    police_filed = False
    med_evaluated_at_scene = False
    taken_to_hos_from_scene = False
    seeked_care_afterward = False

    geom = ""

    gender = ""
    age = 0
    ethnicity = ""
    race = ""

    def __init__(self, form):

        self.gender = ""
        self.age = 0
        self.ethnicity = ""
        self.race = ""

        # parse date
        acc_date_str_ms = form['answer_date'] # in string of milliseconds since midnight Jan 1 1970
        time_ts = time.gmtime(long(acc_date_str_ms)/1000.0)
        self.acc_date = datetime.datetime.fromtimestamp(time.mktime(time_ts))

        # parse "state, city, street, cross_street"
        state_city_st_cst = form['answer_state_city_st_cst']
        if len(state_city_st_cst) !=0 :
            state_city_st_cst_list = state_city_st_cst.split(", ")
            self.state = state_city_st_cst_list[0].strip()
            self.city = state_city_st_cst_list[1].strip()
            self.street = state_city_st_cst_list[2].strip()
            self.cross_street = state_city_st_cst_list[3].strip()

        # parse answer 1 ~ 6 :
        answer_list = []
        for i in range(1, 7):
            answer_list.append(form['answer' + str(i)])

        self.cartype = answer_list[0]
        self.time_of_day = answer_list[1]
        self.police_filed = True if (answer_list[2] == "Yes") else False
        self.med_evaluated_at_scene = True if (answer_list[3] == "Yes") else False
        self.taken_to_hos_from_scene = True if (answer_list[4] == "Yes") else False
        self.seeked_care_afterward = True if (answer_list[5] == "Yes") else False

        # parse geom
        geo_list_str = form['answer_route']
        geo_list_strs = geo_list_str.split(",")
        geo_str = ""
        for i in range(0, len(geo_list_strs)/2):
            geo_str += geo_list_strs[i * 2]
            geo_str += " "
            geo_str += geo_list_strs[i * 2 + 1]
            if i != (len(geo_list_strs)/2 - 1):
                geo_str += ","
        self.geom = 'LINESTRING(' + geo_str + ')'

        # parse user info
        self.gender = form['answer_gender']
        self.age = form['answer_age']
        self.ethnicity = form['answer_ethnicity']
        self.race = form['answer_race']

        self.printCollisionInfo()

    # insert into collisions table
    def syncToDBWithUid(self, some_engine):

        DB_Session = sessionmaker(bind=some_engine)
        db_session = DB_Session()

        try:
            db_session.execute('''
                INSERT INTO Collisions (
                AccDate, State, City, Street, CrossStreet,
                Cartype, TimeOfDay,
                PoliceFiled, MedEvaluatedAtScene, TakenToHosFromScene, SeekedCareAfterward,
                geom,
                Gender, Age, Ethnicity, Race )
                VALUES (
                :acc_date, :state, :city, :street, :cross,
                :cartype, :time_of_day,
                :police, :med, :taken, :seek,
                :geom,
                :gender, :age, :enth, :race )
                ''', {
                "acc_date":self.acc_date,"state":self.state,"city":self.city, "street":self.street, "cross":self.cross_street,
                "cartype":self.cartype, "time_of_day": self.time_of_day,
                "police":str(self.police_filed), "med":str(self.med_evaluated_at_scene),
                "taken":str(self.taken_to_hos_from_scene), "seek":str(self.seeked_care_afterward),
                "geom":self.geom,
                "gender":self.gender, "age":self.age, "enth":self.ethnicity, "race":self.race
                }
            )
            cur = db_session.execute('''
                SELECT count(*)
                FROM Collisions
                '''
            )
            db_session.commit()
            new_cid = cur.fetchone()
            print "new cid is ", str(new_cid[0])
            self.cid = new_cid;
        except:
            db_session.rollback()
            raise

    def printCollisionInfo(self):
        # check if all passed in are correct
        print "a new collision instance"
        print "cartype", self.cartype
        print "state", self.state
        print "city", self.city
        print "street", self.street
        print "time_of_day", self.time_of_day
        print "cross_street", self.cross_street
        print "police_filed", self.police_filed
        print "med_evaluated_at_scene", self.med_evaluated_at_scene
        print "taken_to_hos_from_scene", self.taken_to_hos_from_scene
        print "seeked_care_afterward", self.seeked_care_afterward
        print "acc_date", self.acc_date
        print "geom", self.geom
        print "gender", self.gender
        print "age", self.age
        print "ethn", self.ethnicity
        print "race", self.race

def adminLogin(name, password):
    cur = g.conn.execute('''
        SELECT pass FROM Users WHERE name=%s LIMIT 1;
        ''', (name, )
        )
    pswd = cur.fetchone()[0]
    print "in adminLogin: name is " + name + "pswd is " + pswd
    print "password is " + password
    if pswd == password :
        return True
    else :
        return False

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = "joyce_secret_hhhh"


##
#DATABASEURI = "sqlite:///test.db"
#DATABASEURI = "postgresql://jz2793:pvs9w@104.196.175.120/postgres"
DATABASEURI = "postgresql://peter:940611@127.0.0.1/geo"
#
# This line creates a database engine that knows how to connect to the URI above
##
engine = create_engine(DATABASEURI)

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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  # print request.args

  #########################
  # example of a database query
  #
  #cursor = g.conn.execute("SELECT *")
  #names = []
  #for result in cursor:
  #  names.append(result['name'])  # can also be accessed using result[0]
  #cursor.close()
  ############################
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

@app.route('/draw_route/', methods=['GET', 'POST'])
def draw_route():
    return render_template("draw_route.html")

# submit_route
@app.route('/submit_route/', methods=['GET', 'POST'])
def submit_route():
    print "in submit_route"
    form = request.form
    collision = Collision(form)
    collision.syncToDBWithUid(engine)
    print collision.cid

    # flash("Your submission is successful. Thank you very much!")
    return render_template("thanks.html")

# admin login
@app.route('/admin_login/', methods=['GET', 'POST'])
def admin_login():
    return render_template("admin_login.html")

# admin interface admin.html
@app.route('/admin_page/', methods=['GET', 'POST'])
def admin_page():

  username = request.form['username']
  pswd = request.form['password']
  print "in login() login info is: ", username, pswd

  logged = adminLogin(username, pswd)

  if logged:
    print "logged"
    # total number
    cur = g.conn.execute('''
    SELECT count(*)
    FROM Collisions
    ''')
    total_number = cur.fetchone()[0]
    cur.close()

    # analyzed number
    cur = g.conn.execute('''
    SELECT count(*)
    FROM Collisions c
    WHERE c.analyzed = 't'
    ''')
    analyzed_number = cur.fetchone()[0]
    cur.close()

    print total_number, analyzed_number
    print type(total_number), type(analyzed_number)

    re = dict(total_number = total_number, analyzed_number = analyzed_number)

    return render_template('admin.html', **re)
  else:
    print "cannot login"
    re = dict(failure = 1)
    return render_template("admin_login.html", **re)

# download all
@app.route('/download/', methods=['POST', 'GET'])
def download():
    cur = g.conn.execute('''
    SELECT ST_asText(c.geom)
    FROM Collisions c
    ''')
    results = cur.fetchall()
    print results
    print type(results[0])
    for a_row in results:
        print a_row
        print type(a_row)
        for a_ele in a_row:
            print a_ele
            print type(a_ele)

    t = Template('''
    <html>
        {% for n in data %}
             <div>{{n}}</div>
        {% endfor %}
    </html>
    ''')
    # return render_template(t, data = results)

    csv = """"REVIEW_DATE","AUTHOR","ISBN","DISCOUNTED_PRICE"
    "1985/01/21","Douglas Adams",0345391802,5.95
    "1990/01/12","Douglas Hofstadter",0465026567,9.95
    "1998/07/15","Timothy ""The Parser"" Campbell",0968411304,18.99
    "1999/12/03","Richard Friedman",0060630353,5.95
    "2004/10/04","Randel Helms",0879755725,4.50"""
    # We need to modify the response, so the first thing we
    # need to do is create a response out of the CSV string
    response = make_response(csv)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=books.csv"
    return response

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
