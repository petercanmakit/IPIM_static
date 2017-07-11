from flask import Flask, session, request, render_template, g, redirect, Response, flash, url_for, make_response
from flask_session import Session
from jinja2 import Template

from IPIM import app
from IPIM.collision import Collision
from IPIM.main import engine

import datetime

from IPIM.ga import *
# ga init
ga_analytics = initialize_analyticsreporting()
ga_response = get_report(ga_analytics)

def adminLogin(name, password):
    cur = g.conn.execute('''
        SELECT pass FROM Users WHERE name=%s LIMIT 1;
        ''', (name, )
        )
    pswd = cur.fetchone()[0]
    # print "in adminLogin: name is " + name + "pswd is " + pswd
    # print "password is " + password
    if pswd == password :
        return True
    else :
        return False

def dateStrNdaysAgo2Date(ndays, later):
    '''get the date objects for date->later and ndays before that
    Args: nadays, later
    Returns: [earlierdate<datetime.date>, laterdate<datetime.date>]
    '''
    laterdatetime = datetime.datetime.now()
    laterdate = laterdatetime.date()
    if later == 'now':
        pass
    else:
        laterdatetime = datetime.datetime.strptime(later, '%Y-%m-%d')
        laterdate = laterdatetime.date()
    earlierdatetime = laterdatetime - datetime.timedelta(days=ndays)
    earlierdate = earlierdatetime.date()
    return [earlierdate, laterdate]

def dateStr2Date(datestr):
    '''
    Args: <string> datestr
    Returns: <datetime.date> dateobject
    '''
    date = datetime.datetime.now().date()
    if datestr == 'now':
        pass
    else:
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d').date()
    return date

def dateobject2str(dateobject, bywhat):
    '''turn a date object into string according to bywhat
    Args:
        @dateobject:
        @bywhat: 'day', 'week', 'month', 'year'
    '''
    if bywhat == 'day':
        return str(dateobject)
    if bywhat == 'week':
        return str(dateobject.year) + '-' + str(dateobject.isocalendar()[1])
    if bywhat == 'month':
        return str(dateobject.year) + '-' + str(dateobject.month)
    if bywhat == 'year':
        return str(dateobject.year)

def getCount(start, end, bywhat): # datetime.date, inclusive
    '''get the number of datasets submmited dated from start to end
    Args:
        start, end: in datetime.date() object,
        bywhat: string -> 'day', 'week', 'month', 'year', 'total'
    Returns:
        [[<label>],[<count>]]
    '''

    if bywhat == 'total':
        cur = g.conn.execute('''
        SELECT count(*)
        from collisions
        ''')
        result = cur.fetchone()[0]
        cur.close()
        return [['total'], [result]]

    labels = []
    counts = []
    cur = g.conn.execute('''
    SELECT date_trunc(%s, submitteddate) as bywhat, count(*)
    from collisions
    where submitteddate >= %s and submitteddate <= %s
    group by bywhat
    order by bywhat
    ''',
    (bywhat, str(start), str(end))
    )
    rows = cur.fetchall()
    cur.close()
    for row in rows:
        labels.append(dateobject2str(row[0].date(), bywhat))
        counts.append(int(row[1]))

    return [labels, counts]

# admin interface admin.html
@app.route('/admin/', methods=['GET', 'POST'])
def admin():
  logged = False
  if request.method == 'POST':
      username = request.form['username']
      pswd = request.form['password']
      # print "in login() login info is: ", username, pswd

      logged = adminLogin(username, pswd)
      if logged:
          session['username'] = username
      else:
          if 'username' in session:
              session.pop('username', None)

  if 'username' in session and session['username'] == 'admin' :
      logged = True

  if logged:
    ######## get datasets count ######### [label array<str>, counts array<int>]
    dates_for_day = dateStrNdaysAgo2Date(7, 'now')
    cnt_day = getCount(dates_for_day[0], dates_for_day[1], 'day')
    dates_for_week = dateStrNdaysAgo2Date(28, 'now')
    cnt_week = getCount(dates_for_week[0], dates_for_week[1], 'week')
    cnt_month = getCount(dateStr2Date('2017-04-01'), 'now', 'month')
    cnt_year = getCount(dateStr2Date('2017-04-01'), 'now', 'year')
    cnt_total = getCount(dateStr2Date('2017-04-01'), 'now', 'total')

    ######## get pageviews ######### [label array<str>, pageviews array<int>]
    pv_day = get_pageviews_array(ga_analytics, '6daysAgo', 'today', 'day')
    pv_week = get_pageviews_array(ga_analytics, '27daysAgo', 'today', 'week')
    pv_month = get_pageviews_array(ga_analytics, '2017-05-01', 'today', 'month')
    pv_year = get_pageviews_array(ga_analytics, '2017-01-01', 'today', 'year')
    pv_total = get_pageviews_array(ga_analytics, '2017-01-01', 'today', 'total')

    re = dict(cnt_day=cnt_day, cnt_week=cnt_week, cnt_month=cnt_month,
              cnt_year=cnt_year, cnt_total=cnt_total,
              pv_day=pv_day, pv_week=pv_week, pv_month=pv_month,
              pv_year=pv_year, pv_total=pv_total)

    return render_template('/admin/index.html', **re)
  else:
    # print "cannot login"
    re = dict(failure = 1)
    return render_template("admin_login.html", **re)


# admin see the collisions
@app.route('/admin/collisions/', methods=['POST', 'GET'])
def collisions():
    re = dict()
    if request.method == 'POST':
        cid = request.form['cid']
        if cid != "":
            cur = g.conn.execute('''
                SELECT ST_asText(c.geom), c.SubmitType
                FROM Collisions c
                WHERE c.cid = %s
            ''', (str(cid),)
            )
            result = cur.fetchone()
            path = lineStringToArray(str(result[0]))
            submittype = str(result[1])
            # print analyzed
            cur.close()
            # re = dict(path = path, collisionId = cid, submittype=submittype)
            re['path'] = path
            re['collisionId'] = cid
            re['submittype'] = submittype
            # print path, cid
            cur.close()

    # worldmap
    cur = g.conn.execute('''
        SELECT ST_AsText(ST_PointN(c.geom,1)), c.cid
        FROM Collisions c
    '''
    )
    # POINT(3 2)
    rows = cur.fetchall()
    cur.close()
    spots = []
    cids = []
    for row in rows:
        spots.append(pointStringToArray(row[0]))
        cids.append(str(row[1]))
    re['spots'] = spots
    re['cids'] = cids

    return render_template('/admin/collisions.html', **re)

def lineStringToArray(line_str): #'LINESTRING(0 0, 1 1, 2 1, 2 2)'
    # in js: var path = []; // [[lat, lng], [lat, lng], ...]

    line_str = line_str.replace("LINESTRING(", "").replace(")","")
    line_strs = line_str.split(",")
    path = []
    for str_pair in line_strs:
        str_pairs = str_pair.split(" ")
        path.append(float(str_pairs[0]))
        path.append(float(str_pairs[1]))
    return path

def pointStringToArray(point_str): # POINT(3 2)
    # return point = [lat, lng]
    # in js: var spots = []; // [[lat, lng], [lat, lng], ...]
    point_str = point_str.replace("POINT(", "").replace(")","")
    point_strs = point_str.split(" ")
    point = []
    point.append(float(point_strs[0]))
    point.append(float(point_strs[1]))
    return point

# download dashboard
@app.route('/admin/download/', methods=['GET'])
def download():
    return render_template("/admin/download.html")

# download all
@app.route('/admin/download_all/', methods=['POST', 'GET'])
def download_all():
    cur = g.conn.execute('''
    SELECT c.cid, ST_asText(c.geom)
    FROM Collisions c
    ORDER BY c.cid
    ''')
    stringIO = StringIO()
    results = cur.fetchall()
    for a_row in results:
        for an_ele in a_row:
            stringIO.write(str(an_ele))
            # stringIO.write(an_ele.encode('utf-8'))
            stringIO.write(',')
        stringIO.seek(-1,2) # SEEK_END = 2
        stringIO.write("\n")
    csv = stringIO.getvalue()
    # We need to modify the response, so the first thing we
    # need to do is create a response out of the CSV string
    response = make_response(csv)
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=query_results.csv"

    return response

# mark_analyze
@app.route('/admin/mark_analyzed/', methods=['POST', 'GET'])
def mark_analyzed():
    # print "in mark_analyzed"
    if request.method == 'POST':
        cid = request.form['cid']
        # print cid, type(cid)
        is_mark = request.form['is_mark']
        if is_mark == 'mark':
            cur = g.conn.execute('''
                UPDATE Collisions
                SET analyzed = true
                WHERE cid = %s;
            ''',(str(cid),) )
        else: # 'unmark'
            cur = g.conn.execute('''
                UPDATE Collisions
                SET analyzed = false
                WHERE cid = %s;
            ''',(str(cid),) )
    return render_template("/admin/mark_analyzed.html")
