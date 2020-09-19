from flask import Flask


def make_app():
    app = Flask(__name__)
    app.config["TESTING"] = False
    return app
