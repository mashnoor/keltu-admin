#!/usr/bin/env python

import json
import os
from pymongo import MongoClient

from flask import Flask
from flask import request
import flask
from time import gmtime, strftime
client = MongoClient()
db = client.keltu
dept_db = db.departments
archivetypes_db = db.archivetypes
archive_db = db.archive


# Flask app should start in global layout
app = Flask(__name__)

@app.route('/dashboard')
def dashboard():
    return flask.render_template('dashboard.html')


@app.route('/adddept', methods=['POST'])
def adddept():
    dept = request.form.get('dept')
    dept_db.insert_one({
        "dept":dept
    })
    return flask.redirect(flask.url_for('departments'))

@app.route('/addarchive', methods=['POST'])
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
    print isFound
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
def departments():
    departments = dept_db.find()
    departments_cpy = dept_db.find()
    return flask.render_template('departments.html', departments=departments, departments_cpy=departments_cpy)

@app.route('/addnewarchive')
def addnewarchive():
    departments = dept_db.find()
    archivetypes = archivetypes_db.find()
    return flask.render_template('addnewarchive.html', departments=departments, archivetypes=archivetypes)

@app.route('/archivetypes')
def archivetypes():
    archivetypes = archivetypes_db.find()
    return flask.render_template('archivetypes.html', archivetypes=archivetypes)

@app.route('/addarchivetype', methods=['POST'])
def addarchivetype():
    type = request.form.get('archivetype')
    archivetypes_db.insert_one({
        "type":type
    })
    return flask.redirect(flask.url_for('archivetypes'))

@app.route('/viewarchive')
def viewarchive():
    archives = archive_db.find()
    return flask.render_template('viewfull.html', archives=archives)


#Deletes
@app.route('/deletetype/<atype>')
def deletetype(atype):
    archivetypes_db.remove({
        "type":atype
    })
    return flask.redirect(flask.url_for('archivetypes'))


@app.route('/deletedept/<dept>')
def deletedept(dept):
    dept_db.remove({
        "dept":dept
    })
    return flask.redirect(flask.url_for('departments'))
@app.route('/deletearchive/<link>')
def deletearchive(link):
    archive_db.remove({
        "link":link
    })
    return flask.redirect(flask.url_for('viewarchive'))

''' Web Hook Don't Touh'''
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    r = {
        "speech":"https://www.google.com\r\nhttps://gmail.com",
        "displayText":"http://www.quanfield.com",
        "source":"facebook",

    }
    r = json.dumps(r, indent=4)

    res = flask.make_response(r)

    res.headers['Content-Type'] = 'application/json'
    return res




if __name__ == '__main__':
    port = 5001

    print("Starting app on port %d" % port)

    app.run(port=port)