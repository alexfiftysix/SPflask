import os

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from data import gigs_list, contact_list
from flask_mysqldb import MySQL
from wtforms import Form, StringField, DecimalField, TextAreaField, PasswordField, validators, DateTimeField
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileRequired, FileField
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = 'secret123'

# Config mySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_password'] = ''
app.config['MYSQL_DB'] = 'StreetPiecesClean'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # return from DB as dictionary
# Init mySQL
mysql = MySQL(app)

gig_list = gigs_list()
contacts = contact_list()


# TODO: Work out file upload (For bg photos for music)
# TODO: Give instructions to users on how to get iframe from Bandcamp/Youtube
# TODO: Generalize delete routes, video+music routes

# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap


@app.route('/')
@app.route('/music')
def music():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM music')
    data = cur.fetchall()
    return render_template('music_db.html', music_players=data)


@app.route('/deleteMusic/<music_id>')
@is_logged_in
def delete_music(music_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM music WHERE id = %s', music_id)
    mysql.connection.commit()
    return redirect('/music')


@app.route('/deleteMusic')
@is_logged_in
def delete_mus():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM music')
    data = cur.fetchall()
    return render_template('deleteMusic.html', music=data)


@app.route('/deleteVideo')
@is_logged_in
def delete_vid():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM videos')
    data = cur.fetchall()
    return render_template('deleteVideo.html', videos=data)


@app.route('/deleteVideo/<vid_id>')
@is_logged_in
def delete_video(vid_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM videos WHERE id = %s', vid_id)
    mysql.connection.commit()
    return redirect('/video')


@app.route('/video')
def video():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM videos')
    data = cur.fetchall()
    return render_template('video.html', videos=data, size=result)


class NewVideoForm(Form):
    name = StringField('Title', [validators.data_required(), validators.Length(min=1, max=100)])
    url = StringField('iframe', [validators.data_required(), validators.Length(min=1, max=500)])


@app.route('/addVideo', methods=['GET', 'POST'])
@is_logged_in
def add_video():
    form = NewVideoForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        url = form.url.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Insert new user
        cur.execute('INSERT INTO videos(name, url) VALUES(%s, %s)', (name, url))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        mysql.connection.close()

        return redirect('/video')
    return render_template('addVideo.html', form=form)


@app.route('/gigs')
def gigs():
    cur = mysql.connection.cursor()

    future_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE()')
    future_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    past_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK AND DATE < CURDATE()')
    past_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    gigs_num = future_gigs + past_gigs

    return render_template('gigs.html', gigs=future_gigs_data, old_gigs=past_gigs_data, gigs_num=gigs_num)
    # TODO: Work out what to do if no gigs
    # Close connection


@app.route('/deleteGigs')
@is_logged_in
def delete_gigs():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK')

    future_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE()')
    future_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    past_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK AND DATE < CURDATE()')
    past_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    return render_template('deleteGigs.html', gigs=future_gigs_data, old_gigs=past_gigs_data)


@app.route('/deleteGig/<gig_id>')
@is_logged_in
def delete_gig(gig_id):
    print(gig_id)
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM gigs WHERE id = %s", [gig_id])
    mysql.connection.commit()
    return redirect('/gigs')


class NewMusicForm(Form):
    name = StringField('Title', [validators.data_required(), validators.Length(min=1, max=250)])
    iframe = StringField('iframe', [validators.data_required(), validators.Length(min=1, max=500)])
    image = StringField('Image', [validators.data_required(), validators.Length(min=1, max=500)])


@app.route('/addMusic', methods=['GET', 'POST'])
@is_logged_in
def addMusic():
    form = NewMusicForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        iframe = form.iframe.data
        image = form.image.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Insert new user
        cur.execute('INSERT INTO music(name, iframe, image) VALUES(%s, %s, %s)',
                    (name, iframe, image))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        mysql.connection.close()

        return redirect('/music')
    return render_template('addMusic.html', form=form)


@app.route('/contact')
def contact():
    return render_template('contact.html', contacts=contacts)


@app.route('/photos')
@is_logged_in
def photos():
    return render_template('photos.html')


class NewPhotoForm(FlaskForm):
    path = FileField('Photo', validators=[FileRequired()])


@app.route('/addPhoto', methods=['GET', 'POST'])
@is_logged_in
def add_photo():
    form = NewPhotoForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        f = form.path.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.instance_path, 'static/images/gallery', filename
        ))

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO photos(path) VALUES(%s)', filename)
        mysql.connection.commit()
        mysql.connection.close()

        return redirect('photos.html')
    return render_template('addPhoto.html', form=form)


class NewGigForm(Form):
    title = StringField('Title', [validators.data_required(), validators.Length(min=1, max=250)])
    location = StringField('Location', [validators.data_required(), validators.Length(min=1, max=250)])
    date = DateField('Date', [validators.data_required()])
    price = DecimalField('Price', [validators.data_required()])
    link = StringField('Link', [validators.Length(min=0, max=250)])


@app.route('/addGig', methods=['GET', 'POST'])
@is_logged_in
def add_gig():
    form = NewGigForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        location = form.location.data
        date = form.date.data
        price = form.price.data
        link = form.link.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Insert new user
        cur.execute('INSERT INTO gigs(title, location, date, price, link) VALUES(%s, %s, %s, %s, %s)',
                    [title, location, date, price, link])

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        mysql.connection.close()

        return redirect('/gigs')
        return render_template('addGig.html', form=form)  # todo: replace this
    return render_template('addGig.html', form=form)


class NewUserForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=250)])
    password = PasswordField('Password', [
        validators.data_required(),
        validators.Length(min=8, max=250)
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/addUser', methods=['GET', 'POST'])
@is_logged_in
def add_user():
    form = NewUserForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor
        cur = mysql.connection.cursor()

        # Insert new user
        cur.execute('INSERT INTO users(username, password) VALUES(%s, %s)', (username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        mysql.connection.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('/music'))
    return render_template('addUser.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        # not using wtForms
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute('SELECT * FROM users WHERE username = %s', [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed

                session['logged_in'] = True
                session['username'] = username

                return redirect('/')
            else:
                app.logger.info('PASSWORD INCORRECT')
                error = 'Username or password incorrect'
                return render_template('login.html', error=error)

        else:
            error = 'Username or password incorrect'
            app.logger.info('NO USER')
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)
