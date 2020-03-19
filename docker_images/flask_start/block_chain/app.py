

from flask import Flask
import flask
from flask import Flask
from flask import render_template,jsonify
from flask_httpauth import HTTPDigestAuth
from flask import request, session

from block_chain.blueprints.page import construct_page_blueprint

def get_pw( username):
       
       print(username)
       return "not"
#       if username in self.users:
#           print("sucess")
#           return self.users[username]
#       return None

def create_app():
    """
    Create a Flask application using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)
    app.auth = HTTPDigestAuth()
    app.auth.get_password( get_pw )
    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)
    page = construct_page_blueprint(app)
    app.register_blueprint(page)

    return app
