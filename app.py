from flask import Flask, render_template
from data import gigs_list, contact_list

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


if __name__ == '__main__':
    app.run(debug=True)
