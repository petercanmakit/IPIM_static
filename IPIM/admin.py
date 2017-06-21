from flask import Flask, session, request, render_template, g, redirect, Response, flash, url_for, make_response
from flask_session import Session
from jinja2 import Template


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
    # print "logged"
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

    # daytime number
    cur = g.conn.execute('''
    SELECT count(*)
    FROM Collisions c
    WHERE c.TimeOfDay = 'Day time'
    ''')
    daytime_number = cur.fetchone()[0]
    cur.close()

    # nighttime number
    # nighttime_number = total_number - daytime_number

    re = dict(total_number = total_number, analyzed_number = analyzed_number, daytime_number = daytime_number)

    return render_template('/admin/index.html', **re)
  else:
    # print "cannot login"
    re = dict(failure = 1)
    return render_template("admin_login.html", **re)


# admin see the collisions
@app.route('/admin/collisions/', methods=['POST', 'GET'])
def collisions():
    if request.method == 'POST':
        cid = request.form['cid']
        if cid != "":
            cur = g.conn.execute('''
                SELECT ST_asText(c.geom), c.analyzed
                FROM Collisions c
                WHERE c.cid = %s
            ''', (str(cid),)
            )
            result = cur.fetchone()
            path = lineStringToArray(str(result[0]))
            analyzed = str(result[1])
            # print analyzed
            cur.close()

            re = dict(path = path, collisionId = cid, analyzed = analyzed)
            # print path, cid
            cur.close()
            return render_template('/admin/collisions.html', **re)
    # print "just get"
    return render_template('/admin/collisions.html')

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
