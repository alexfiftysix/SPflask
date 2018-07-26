from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from data import gigs_list, contact_list
from flask_mysqldb import MySQL
from wtforms import Form, StringField, DecimalField, TextAreaField, PasswordField, DateField, validators, DateTimeField, \
    FileField
from passlib.hash import sha256_crypt
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


# TODO: Remove music/gigs/video routes
# TODO: Give instructions on how to get iframe from Bandcamp/Youtube

@app.route('/')
@app.route('/music')
def music():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM music')
    data = cur.fetchall()
    return render_template('music_db.html', music_players=data)
    mysql.connection.close()


@app.route('/video')
def video():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM videos')
    data = cur.fetchall()
    return render_template('video.html', videos=data, size=result)


class NewVideoForm(Form):
    name = StringField('Title', [validators.data_required(), validators.Length(min=1, max=100)])
    url = StringField('url', [validators.data_required(), validators.Length(min=1, max=500)])


@app.route('/addVideo', methods=['GET', 'POST'])
def addVideo():
    form = NewVideoForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        url = form.url.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Insert new user
        cur.execute('INSERT INTO videos(name, url) VALUES(%s, %s)',
                    (name, url))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        mysql.connection.close()

        return redirect('/video')
    return render_template('addVideo.html', form=form)


@app.route('/gigs')
def gigs():
    cur = mysql.connection.cursor()

    result = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK')

    future_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE()')
    future_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    past_gigs = cur.execute('SELECT * FROM gigs WHERE DATE >= CURDATE() - INTERVAL 1 WEEK AND DATE < CURDATE()')
    past_gigs_data = sorted(cur.fetchall(), key=lambda k: k['date'])

    if result > 0:
        return render_template('gigs.html', gigs=future_gigs_data, old_gigs=past_gigs_data)
    # Close connection
    mysql.connection.close()


class NewMusicForm(Form):
    name = StringField('Title', [validators.data_required(), validators.Length(min=1, max=250)])
    iframe = StringField('iframe', [validators.data_required(), validators.Length(min=1, max=500)])
    image = StringField('Image', [validators.data_required(), validators.Length(min=1, max=500)])


@app.route('/addMusic', methods=['GET', 'POST'])
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
def photos():
    return render_template('photos.html')


class NewPhotoForm(Form):
    title = StringField('Title', [validators.data_required(), validators.Length(min=1, max=250)])
    photo = FileField('Photo', [validators.data_required()])
    gallery = StringField('Gallery')


class NewGigForm(Form):
    title = StringField('Title', [validators.data_required(), validators.Length(min=1, max=250)])
    location = StringField('Location', [validators.data_required(), validators.Length(min=1, max=250)])
    date = DateTimeField('Date', [validators.data_required()])
    price = DecimalField('Price', [validators.data_required()])
    link = StringField('Link', [validators.data_required(), validators.Length(min=0, max=250)])


@app.route('/addGig', methods=['GET', 'POST'])
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
                    (title, location, date, price, link))

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

        return redirect(url_for('music.html'))
    return render_template('addUser.html', form=form)


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)
