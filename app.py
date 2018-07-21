from flask import Flask, render_template
from data import Gigs_list

app = Flask(__name__)

Gigs_list = Gigs_list()


@app.route('/')
@app.route('/music')
def music():
    return render_template('music.html')


@app.route('/video')
def video():
    return render_template('video.html')


@app.route('/gigs')
def gigs():
    return render_template('gigs.html', gigs=Gigs_list)


if __name__ == '__main__':
    app.run(debug=True)
