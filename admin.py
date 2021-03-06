

import json
import os
from pymongo import MongoClient
from flask import session
from flask import Flask
from flask import request
import flask
from time import gmtime, strftime
import flask_login
login_manager = flask_login.LoginManager()
client = MongoClient()
db = client.keltu
dept_db = db.departments
archivetypes_db = db.archivetypes
archive_db = db.archive


# Flask app should start in global layout
app = Flask(__name__)
app.secret_key = 'super secret string'
login_manager.init_app(app)
users = {'keltu': {'password': 'keltu9876', 'role':'Super Admin'},
        'Sawrup': {'password': 'sawrup4455', 'role':'Admin'},
        'Bhubon': {'password': 'bhubon9871', 'role':'Admin'},
        'Rahat': {'password': 'rahat4780', 'role':'Admin'}
    }

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    flask_login.login_user(user)

    return user


'''Web'''


'''Authetication Processes'''
@app.route('/')
def index():
    return flask.redirect(flask.url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
         return flask.render_template('login.html')

    username = flask.request.form['username']
    if flask.request.form['password'] == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('dashboard'))

    return "Your credentials didn't match :3"

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return flask.redirect(flask.url_for('login'))

''' View Processes'''
@app.route('/dashboard')
@flask_login.login_required
def dashboard():

        return flask.render_template('dashboard.html')



@app.route('/adddept', methods=['POST'])
@flask_login.login_required
def adddept():
    dept = request.form.get('dept')
    dept_db.insert_one({
        "dept":dept
    })
    return flask.redirect(flask.url_for('departments'))

@app.route('/addarchive', methods=['POST'])
@flask_login.login_required
def addarchive():
    title = str(request.form.get('title')).strip()
    department = str(request.form.get('department')).strip()
    subject = str(request.form.get('subject')).strip()
    archivetype = str(request.form.get('archivetype')).strip()
    semester = str(request.form.get('semester')).strip()
    teachersname = str(request.form.get('teachersname')).strip()
    link = str(request.form.get('link')).strip()
    isFound = dept_db.find_one({
        "dept":department,
        "subjects":subject
    })
    #print isFound
    if isFound is None:
        msg = "Subject " + subject + " is not added in " + department + " department. Add it and try again."
        return flask.render_template('addresult.html', success=False, msg=msg)

    else:
        archive_db.insert_one({
            "title":title,
            "department":department,
            "subject":subject,
            "archivetype":archivetype,
            "semester":semester,
            "teachersname":teachersname,
            "link":link,
            "time":strftime("%Y-%m-%d %H:%M:%S", gmtime())
        })
        return flask.render_template('addresult.html', success=True)



@app.route('/addsubject', methods=['POST'])
@flask_login.login_required
def addsubject():
    dept = request.form.get('dept')
    subject = request.form.get('subject')
    db.departments.update({
        "dept":dept
    },
    {
        "$push": {"subjects":subject}
    })
    return flask.redirect(flask.url_for('departments'))

@app.route('/departments')
@flask_login.login_required
def departments():
    departments = dept_db.find()
    departments_cpy = dept_db.find()
    return flask.render_template('departments.html', departments=departments, departments_cpy=departments_cpy)

@app.route('/addnewarchive')
@flask_login.login_required
def addnewarchive():
    departments = dept_db.find()
    archivetypes = archivetypes_db.find()
    return flask.render_template('addnewarchive.html', departments=departments, archivetypes=archivetypes)

@app.route('/archivetypes')
@flask_login.login_required
def archivetypes():
    archivetypes = archivetypes_db.find()
    return flask.render_template('archivetypes.html', archivetypes=archivetypes)

@app.route('/addarchivetype', methods=['POST'])
@flask_login.login_required
def addarchivetype():
    type = request.form.get('archivetype')
    archivetypes_db.insert_one({
        "type":type
    })
    return flask.redirect(flask.url_for('archivetypes'))

@app.route('/viewarchive', methods=['GET', 'POST'])
@flask_login.login_required
def viewarchive():
    departments = dept_db.find()
    if flask.request.method == 'POST':
        session['viewwhat'] = request.form.get('viewwhat')
        session['semester'] = request.form.get('semester')
        session['subject'] = request.form.get('subject')
        session['archivetype'] = request.form.get('archivetype')

    dept_session_val = session.get('viewwhat', 'all')
    semester_session_val = session.get('semester', 'all')
    subject_session_val = session.get('subject', 'all')
    archivetype_session_val = session.get('archivetype', 'all')
    find_dict = {}
    if dept_session_val != 'all':
        find_dict['department'] = dept_session_val
    if semester_session_val != 'all':
        find_dict['semester'] = semester_session_val
    if subject_session_val != 'all' and subject_session_val!= '':
        find_dict['subject'] = subject_session_val
    if archivetype_session_val != 'all':
        find_dict['archivetype'] = archivetype_session_val

    archives = archive_db.find(find_dict)
    types = archivetypes_db.find()


    return flask.render_template('viewfull.html', archives=archives, departments=departments, types=types)

#Edit Archive
@app.route('/editarchive/<time>')
def editarchive(time):
    departments = dept_db.find()
    archivetypes = archivetypes_db.find()

    entry = archive_db.find_one({
        'time':time
    })
    print(entry['title'])
    return flask.render_template('editarchive.html', departments=departments, archivetypes=archivetypes, entry=entry)

#Update
@app.route('/updatearchive', methods=['POST'])
def updatearchive():
   
    title = str(request.form.get('title')).strip()
    department = str(request.form.get('department')).strip().lower()
    subject = str(request.form.get('subject')).strip().lower()
    archivetype = str(request.form.get('archivetype')).strip()
    semester = str(request.form.get('semester')).strip().lower()
    teachersname = str(request.form.get('teachersname')).strip()
    link = str(request.form.get('link')).strip()
    isFound = dept_db.find_one({
        "dept": department,
        "subjects": subject
    })
    # print isFound
    if isFound is None:
        msg = "Subject " + subject + " is not added in " + department + " department. Add it and try again."
        return flask.render_template('addresult.html', success=False, msg=msg)

    else:
        archive_db.remove({
        "time": request.form.get('time')
        })
        archive_db.insert_one({
            "title": title,
            "department": department,
            "subject": subject,
            "archivetype": archivetype,
            "semester": semester,
            "teachersname": teachersname,
            "link": link,
            "time": strftime("%Y-%m-%d %H:%M:%S", gmtime())
        })
        return flask.render_template('addresult.html', success=True)

#Deletes
@app.route('/deletetype/<atype>')
@flask_login.login_required
def deletetype(atype):
    archivetypes_db.remove({
        "type":atype
    })
    return flask.redirect(flask.url_for('archivetypes'))


@app.route('/deletedept/<dept>')
@flask_login.login_required
def deletedept(dept):
    dept_db.remove({
        "dept":dept
    })
    return flask.redirect(flask.url_for('departments'))
@app.route('/deletearchive/<time>')
@flask_login.login_required
def deletearchive(time):
    archive_db.remove({
        "time":time
    })
    return flask.redirect(flask.url_for('viewarchive'))

''' Web Hook Don't Touh'''
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Etering Webhook")
    req = request.get_json(silent=True, force=True)
    dept = req["result"]["parameters"]["department"]
    subject = req["result"]["parameters"]["subjects"]
    semester = req["result"]["parameters"]["semester"]
    type = req["result"]["parameters"]["Academy"]



    print(req)
    #print(dept)
    #print(subject)
    #print(semester)
    #print(type)
    archives = archive_db.find({
        "department":dept,
        "archivetype":type,
        "semester":semester,
        "subject":subject
    })
    #print(archives.count())
    if archives.count() == 0:
        return generate_response("Sorry, I don't have the " + subject + " " + type + " :'( :(")
    else:
        result = "Here's what I have for you <3 \r\n\r\n"
        for archive in archives:
            result+= archive['title'] + " By " + archive['teachersname'] + "\r\n"
            result+= "Link: " + archive['link'] + "\r\n\r\n"
        return generate_response(result)

    #print("Request:")
    resp = json.dumps(req, indent=4)
    #print(resp)

    return generate_response("hello")


def generate_response(text):
    r = {
        "speech":text,
        "displayText":"http://www.quanfield.com",
        "source":"facebook",

    }
    r = json.dumps(r, indent=4)
    res = flask.make_response(r)
    res.headers['Content-Type'] = 'application/json'
    return res


if __name__ == '__main__':
    port = 5002

    #print("Starting app on port %d" % port)

    app.run(port=port)
    #app.run(host='0.0.0.0', port=port)
