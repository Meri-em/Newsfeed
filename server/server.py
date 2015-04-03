from flask import (Flask, render_template, request, session, flash, redirect,
                   url_for, send_file)
from wtforms.fields import TextAreaField, SubmitField, FileField
from wtforms import Form, validators, TextField, PasswordField
from werkzeug import generate_password_hash, check_password_hash, secure_filename
from datetime import datetime
from json import dumps
from server.db import NewsfeedDB
from bson.objectid import ObjectId

from server.forms import RegistrationForm, LoginForm
db = NewsfeedDB()


app = Flask(__name__)
app.secret_key = b'\x12\xc24\xb9\x80\xa8\xe9\xbc\x1c\x8e\x82\x0ez\xb16\xf3<\xad\xab\x15\xd9\x18\xfc\xa4'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        if not db.find_user(username):
            db.add_user(username, password)
            return render_template('register.html', success=True)
        else:
            flash("Потребителското име вече е заето. Изберете ново")
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user_doc = db.find_user(username)
        passwords_match = check_password_hash(user_doc['password'], password)

        if user_doc and passwords_match:
            session['user'] = username
            return redirect(url_for('messages'))
        else:
            flash("Грешно потребителско име или парола")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/avatar/<username>')
def user_avatar(username):
    return send_file(db.get_avatar(username), mimetype='image/jpeg')


@app.route('/leaderboard')
def leaderboard():
    _users = list(db.get_users())
    ratings = [(e['number_of_likes']/(e['number_of_blocks']**2 + 1), e['username']) for e in _users]
    ratings.sort()
    data = [{'username': e[1], 'rating': int(e[0])} for e in reversed(ratings)]
    return render_template('leaderboard.html', data=data)




@app.route('/messages', defaults={'limit': 20})
@app.route('/messages/<int:limit>')
def messages(limit):
    presented = reversed(list(db.get_messages(session['user'], limit)))
    return render_template('messages.html', data=presented)


@app.route('/messages.json', defaults={'limit': 20})
@app.route('/messages/<int:limit>.json')
def messages_json(limit):
    _messages = list(reversed(list(db.get_messages(session['user'], limit))))
    result = []
    for e in _messages:
        result.append({
            '_id': str(e['_id']),
            'author': e['author'],
            'likes': len(e['likes']),
            'date_time': str(e['date_time']),
            'message': e['message']
        })

    return dumps(result)


@app.route('/messages/new', methods=['POST'])
def add_message():
    db.add_message(session['user'], request.json['message'])
    return messages_json()


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            db.update_avatar(session['user'], file)
    return render_template('profile.html', username=session['user'])

@app.route('/users', methods=['GET'])
def users():
    blocked = db.view_profile(session['user'])['blocked_users']
    _users = [e['username'] for e in db.get_users()]
    _users = [{"username": e, "blocked": (e in blocked)} for e in _users]

    return render_template('users.html', data=_users)


@app.route('/block/<blocked_user>', methods=['POST'])
def block(blocked_user):
    if db.find_user(blocked_user):
        db.block_user(session['user'], blocked_user)
    return ""


@app.route('/unblock/<blocked_user>', methods=['POST'])
def unblock(blocked_user):
    db.unblock_user(session['user'], blocked_user)
    return ""

@app.route('/like/<message_id>', methods=['POST'])
def like_message(message_id):
    db.like_message(session['user'], message_id)
    return "1"


if __name__ == '__main__':
    app.run(debug = True)