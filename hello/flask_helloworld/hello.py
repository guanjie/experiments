from flask import Flask, url_for
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route("/", methods=['get', 'post'])
def index():
    if request.method == "post":
        return render_template("posthello.html")
    else:
        return render_template("hello.html")  # % ("guanjie")


@app.route("/hello/<username>")
def hello(username):
    return "Hello %s!" % username


@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/about')
def about():
    return 'The about page'


with app.test_request_context():
    print url_for("index")

if __name__ == "__main__":
    app.run(debug=True)
