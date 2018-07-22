from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import gigs_list, contact_list
from flask_mysqldb import MySQL
from wtforms import Form, StringField, DecimalField, TextAreaField, PasswordField, DateField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

gig_list = gigs_list()
contacts = contact_list()


@app.route('/')
@app.route('/music')
def music():
    return render_template('music.html')


@app.route('/video')
def video():
    return render_template('video.html')


@app.route('/gigs')
def gigs():
    return render_template('gigs.html', gigs=gig_list)


@app.route('/contact')
def contact():
    return render_template('contact.html', contacts=contacts)


@app.route('/photos')
def photos():
    return render_template('photos.html')


class NewGigForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=250)])
    location = StringField('Location', [validators.Length(min=1, max=250)])
    date = DateField('Date', [validators.DataRequired])
    price = DecimalField('Price', [validators.number_range(min=0, max=999999)])
    link = StringField('Link', [validators.Length(min=0, max=250)])


@app.route('/addGig', methods=['GET', 'POST'])
def add_gig():
    form = NewGigForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('addGig.html', form=form) #todo: replace this
    return render_template('addGig.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
