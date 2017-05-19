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
from flask import Flask, session, request, render_template, g, redirect, Response, flash, url_for
from flask_session import Session

import datetime
import time

class User(object):
    """
    """
    uid = long(-1)
    name = ""
    email = ""
    password = ""
    gender = ""
    birthdate = None # d1 = datetime.date(2008,3,1)
    ethnicity = ""
    race = ""

    def __init__(self, email, password):
        """Return a User object"""
        self.email = email
        self.password = password

    def register(self, name, gender, birthdate, ethnicity, race):
        """If it's a new user, register for it. return its uid
        """
        print "in register"
        cur = g.conn.execute('''
        SELECT 1 FROM Users WHERE Email=%s LIMIT 1;
        ''', (self.email, )
        )
        for row in cur:
            print row[0]
            if row[0] == 1:
                print "This email already registed!"
                cur.close()
                return -1
            else :
                pass
        cur.close()
        self.name = name
        if gender == 'Female ':
            self.gender = 'female'
        else:
            self.gender = 'male'
        # birthdate str "YYYY-MM-DD"
        birthdates = birthdate.split("-")
        self.birthdate = datetime.date(int(birthdates[0]), int(birthdates[1]) ,int(birthdates[2]))
        self.ethnicity = ethnicity
        self.race = race
        cur = g.conn.execute('''
        INSERT INTO Users (Name,Email,Pass,Gender,Birthdate,Ethnicity,Race)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ''', (name, self.email, self.password, gender,
        birthdate, ethnicity, race)
        )
        cur.close()
        cur = g.conn.execute('''
        SELECT u.Uid
        FROM Users u
        WHERE u.Email = %s
        ''', (self.email, )
        )
        for row in cur:
            self.uid = row[0]
        cur.close()
        print "Registed successfully, uid is ", self.uid
        return self.uid

    def login(self):
        """Login in, return uid"""
        cur = g.conn.execute('''
        SELECT pass FROM Users WHERE Email=%s LIMIT 1;
        ''', (self.email, )
        )
        if cur.rowcount == 0:
            print "no such user ", self.email
            return -1
        elif self.password == cur.fetchone()[0]:
            print "login successfully! ", self.email
            cur.close()
            cur = g.conn.execute('''
            SELECT uid, name, gender, birthdate, ethnicity, race FROM Users WHERE Email=%s LIMIT 1;
            ''', (self.email, )
            )
            if(cur.rowcount != 0):
                row = cur.fetchone();
                self.uid = row[0]
                self.name = row[1]
                self.gender = row[2]
                self.birthdate = row[3] # date()
                self.ethnicity = row[4]
                self.race = row[5]
            else:
                self.uid = -1 # no such email
            cur.close()
            return self.uid
        else:
            print "wroing password ", self.email
            return -1 # wrong password

class Collision(object):
    """docstring for Collision."""
    cid = long(-1)
    cartype = ""
    city = ""
    street = ""
    cross_street = ""
    police_filed = False
    med_evaluated_at_scene = False
    taken_to_hos_from_scene = False
    seeked_care_afterward = False
    acc_date = None
    geom = ""
    uid = long(-1)

    def __init__(self, answers_list, geo_list_str, acc_date_str_ms, st_cst_city):
        self.cartype = answers_list[0]
        self.police_filed = True if (answers_list[1] == "Yes") else False
        self.med_evaluated_at_scene = True if (answers_list[2] == "Yes") else False
        self.taken_to_hos_from_scene = True if (answers_list[3] == "Yes") else False
        self.seeked_care_afterward = True if (answers_list[4] == "Yes") else False
        geo_list_strs = geo_list_str.split(",")
        geo_str = ""
        for i in range(0, len(geo_list_strs)/2):
            geo_str += geo_list_strs[i * 2]
            geo_str += " "
            geo_str += geo_list_strs[i * 2 + 1]
            if i != (len(geo_list_strs)/2 - 1):
                geo_str += ","
        self.geom = 'LINESTRING(' + geo_str + ')'
        if len(st_cst_city) !=0 :
            st_cst_city_list = st_cst_city.split(", ")
            self.street = st_cst_city_list[0].strip()
            self.cross_street = st_cst_city_list[1].strip()
            self.city = st_cst_city_list[2].strip()
        time_ts = time.gmtime(long(acc_date_str_ms)/1000.0)
        self.acc_date = datetime.datetime.fromtimestamp(time.mktime(time_ts))
        self.printCollisionInfo()


    # insert into collisions table
    def syncToDBWithUid(self, uid, some_engine):
        self.uid = uid

        DB_Session = sessionmaker(bind=some_engine)
        db_session = DB_Session()

        try:
            db_session.execute('''
                INSERT INTO Collisions (City,Street,CrossStreet,Cartype,PoliceFiled,
                MedEvaluatedAtScene,TakenToHosFromScene,SeekedCareAfterward,geom,Uid)
                VALUES (:city,:street,:cross,:cartype,:police,:med,:taken,:seek,:geom,:uid)
                ''', {"city":self.city, "street":self.street, "cross":self.cross_street, "cartype":self.cartype,
                "police":str(self.police_filed), "med":str(self.med_evaluated_at_scene),
                "taken":str(self.taken_to_hos_from_scene), "seek":str(self.seeked_care_afterward),
                "geom":self.geom, "uid":str(self.uid) }
            )
            cur = db_session.execute('''
                SELECT count(*)
                FROM Collisions
                '''
            )
            db_session.commit()
            new_cid = cur.fetchone()
            print "new cid is ", str(new_cid[0])
        except:
            db_session.rollback()
            raise

    def printCollisionInfo(self):
        # check if all passed in are correct
        print "a new collision instance"
        print "cartype", self.cartype
        print "city", self.city
        print "street", self.street
        print "cross_street", self.cross_street
        print "police_filed", self.police_filed
        print "med_evaluated_at_scene", self.med_evaluated_at_scene
        print "taken_to_hos_from_scene", self.taken_to_hos_from_scene
        print "seeked_care_afterward", self.seeked_care_afterward
        print "acc_date", self.acc_date
        print "geom", self.geom


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = "joyce"


#
# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
#DATABASEURI = "sqlite:///test.db"
#DATABASEURI = "postgresql://jz2793:pvs9w@104.196.175.120/postgres"
DATABASEURI = "postgresql://peter:940611@127.0.0.1/geo"


#
# This line creates a database engine that knows how to connect to the URI above
#
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

  if 'username' in session:
      username = session['username']
      return render_template("index.html", username = username)


  return render_template("index.html")

@app.route('/signup', methods=['POST'])
def signup():
  email = request.form['email']
  print "in signup() email is ", email
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  # print request.args

  return render_template("signup.html", email = email)

@app.route('/trysignup', methods=['POST'])
def trysignup():
  email = request.form['email']
  nickname = request.form['nickname']
  pwd = request.form['pwd']
  gender = request.form['gender']
  bod = request.form['bod']
  ethn = request.form['ethn']
  race = request.form['race']

  print "in trysignup() signup info is: ", email, nickname, pwd, gender, bod, ethn, race
  # create a new user instance
  user = User(email, pwd)
  registered = user.register(nickname, gender, bod, ethn, race)
  if registered > 0:
    print "new uid is ", user.uid
    re = dict(nickname = nickname, success = 1)
    return render_template("signup.html", **re)
  else:
    print "cannot register", user.uid
    re = dict(email = email, registered = 1)
    return render_template("signup.html", **re)

@app.route('/draw_route', methods=['GET', 'POST'])
def draw_route():
    print "in draw_route"
    username = None
    try:
        if session['username']:
            print session['username']
            username = session['username']
    except Exception as e:
        print "session no username"

    return render_template("draw_route.html", username = username)

# submit_route
@app.route('/submit_route', methods=['GET', 'POST'])
def submit_route():
    print "in submit_route"
    username = None
    try:
        if session['username']:
            print session['username']
            username = session['username']
    except Exception as e:
        print "session no username"

    answers = []
    for i in range(1, 6):
        answers.append(request.form['answer' + str(i)])
    print answers
    acc_date = request.form['answer_date'] # in string of milliseconds since midnight Jan 1 1970
    geom = request.form['answer_route']
    st_cst_city = request.form['answer_st_cst_city']
    print "acc date", acc_date
    print "geometry", geom
    print "st_cst_city", st_cst_city

    # answers_list, geo_list_str, acc_date_str_ms, st_cst_city
    collision = Collision(answers, geom, acc_date, st_cst_city)
    try:
        if session['username']:
            uid = long(session['uid'])
            collision.syncToDBWithUid(uid, engine)
            return render_template("draw_route.html", username = username, submit_success = 1)
    except Exception as e:
        print "not logged in"
        return render_template("draw_route.html", not_logged = 1)
    return redirect("/")



@app.route('/login', methods=['POST'])
def login():
  email = request.form['email']
  pwd = request.form['pwd']

  print "in login() login info is: ", email, pwd
  # create a new user instance
  user = User(email, pwd)
  logged = user.login()
  print logged
  if logged > 0:
    print "logged, the uid is ", user.uid
    re = dict(nickname = user.name, success = 1)
    session['username'] = user.name
    session['uid'] = user.uid
    print "in session"
    print session['username']
    print session['uid']
    return redirect('/')
  else:
    print "cannot login", user.uid
    re = dict(failure = 1)
    return render_template("signup.html", **re)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('uid', None)
    return redirect('/')

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
