from flask import Flask, render_template
from data import Articles, Gigs_list

app = Flask(__name__)

Articles = Articles()
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
    return render_template('gigs.html', articles=Articles, gigs=Gigs_list)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', articles=Articles, id=id)


if __name__ == '__main__':
    app.run(debug=True)
