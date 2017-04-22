"""
    mychat built for ASAPP backend challenge

    authored by Nicholas Matthews

"""

import sqlite3
import datetime
import os
from flask import Flask, g, render_template, flash, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'mychat.db'
USERS_TABLE = "users"
MESSAGES_TABLE = "messages"
USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"
SENDER_FIELD = "sender"
RECIPIENT_FIELD = "recipient"
MEDIA_FIELD = "media"
TXT_MEDIA = "TXT"
IMG_MEDIA = "IMG"
VID_MEDIA = "VID"
METADATA_FIELD = "metadata"
MESSAGE_FIELD = "body"
DATETIME_FIELD = "date_time"
FORMAT = '%Y-%m-%d %H:%M:%S'

app = Flask(__name__)


app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'mychat.db'),
    SECRET_KEY='development key'
))

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Successfully initialized the database.')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

##### DB Convenience #####

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def edit_db(edit, args=(), one=False):
    db = get_db()
    try:
        db.execute(edit, args)
        db.commit()
        flash("Edit successfully committed")
        return True
    except sqlite3.Error as e:
        print ("An error occurred:", e.args[0])
        return False

def query_username(username):
    query = 'SELECT * FROM %s WHERE %s = ?' % (USERS_TABLE, USERNAME_FIELD)
    return query_db(query, (username,))

def check_login(username, password):
    query = "SELECT %s, %s FROM %s WHERE %s = ?" % (USERNAME_FIELD, PASSWORD_FIELD, USERS_TABLE, USERNAME_FIELD)
    args = (username,)
    user = query_db(query, args, True)
    if user is None or user == []:
        return (False, "Username not valid.")
    if check_password_hash(user[PASSWORD_FIELD], password):
        return (True, "")
    return (False, "Password incorrect.")

# REQUIRED REQUEST "FETCH MESSAGES"
def query_messages_between(user_a, user_b, perpage=0, page=0):
    offset = perpage * page
    query = 'SELECT * FROM %s \
                 WHERE (%s = ? AND %s = ?) \
                 OR (%s = ? AND %s = ?) \
                 ORDER BY %s' % (MESSAGES_TABLE, SENDER_FIELD, RECIPIENT_FIELD, \
                 SENDER_FIELD, RECIPIENT_FIELD, DATETIME_FIELD)
    if perpage != 0:
        query += " LIMIT " + str(offset) + ", " + str(perpage)
    args = (user_a, user_b, user_b, user_a)
    return query_db(query, args)

# REQUIRED REQUEST "SEND MESSAGE"
def insert_message(sender, recipient, body, media='TXT', metadata=''):
    queried_sender = query_username(sender)
    queried_recipient = query_username(recipient)
    if queried_sender == [] or queried_recipient == []:
        return (False, "Invalid username used.")
    now = datetime.datetime.now()
    now_formatted = now.strftime(FORMAT)
    success = (False, "")
    if media == TXT_MEDIA:
        insert = "INSERT INTO %s(%s, %s, %s, %s, %s) VALUES (?, ?, ?, ?, ?)" % (MESSAGES_TABLE, \
                    SENDER_FIELD, RECIPIENT_FIELD, MEDIA_FIELD, MESSAGE_FIELD, DATETIME_FIELD)
        args = (sender, recipient, TXT_MEDIA, body, now_formatted)
        success = edit_db(insert, args)
    elif media == IMG_MEDIA:
        insert = "INSERT INTO %s(%s, %s, %s, %s, %s, %s) VALUES (?, ?, ?, ?, ?, ?)" % (MESSAGES_TABLE, \
                    SENDER_FIELD, RECIPIENT_FIELD, MEDIA_FIELD, METADATA_FIELD, MESSAGE_FIELD, DATETIME_FIELD)
        args = (sender, recipient, IMG_MEDIA, "250, 250", body, now_formatted)
        success = edit_db(insert, args)
    elif media == VID_MEDIA:
        insert = "INSERT INTO %s(%s, %s, %s, %s, %s, %s) VALUES (?, ?, ?, ?, ?, ?)" % (MESSAGES_TABLE, \
                    SENDER_FIELD, RECIPIENT_FIELD, MEDIA_FIELD, METADATA_FIELD, MESSAGE_FIELD, DATETIME_FIELD)
        args = (sender, recipient, VID_MEDIA, "1m2s, YouTube", body, now_formatted)
        success = edit_db(insert, args)
    if success:
        return (True, "Message sent!")
    else:
        return (False, "Message failed to send.")

# REQUIRED REQUEST "CREATE USER"
def insert_user(username, password):
    users = query_username(username)
    if users == []:
        insert = 'INSERT INTO %s (%s, %s) VALUES (?, ?)' % (USERS_TABLE, USERNAME_FIELD, PASSWORD_FIELD)
        args = (username, generate_password_hash(password))
        success = edit_db(insert, args)
        if success:
            return (True, "User created!")
        else:
            return (False, "User creation failed")
    else:
        return (False, "User already exists.")

##### App #####

@app.route('/')
def show_messages():
    messages = []
    if 'logged_in' in session and session['logged_in']:
        if 'username' in session:
            messages = query_messages_between(session['username'], 'nick')
    print(messages)
    return render_template('show_messages.html', messages=messages)

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    error = None
    if request.method == 'POST':
        status = insert_user(request.form['username'], request.form['password'])
        if status[0]:
            return redirect(url_for('login'))
        else:
            error = status[1]
    return render_template('add_user.html', error=error)

@app.route('/send', methods=['POST'])
def send_message():
    status = insert_message(session['username'], request.form['recipient'], request.form['body'])
    flash(status[1])
    return redirect(url_for('show_messages'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        status = check_login(request.form['username'], request.form['password'])
        if not status[0]:
            error = status[1]
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_messages'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('show_messages'))
