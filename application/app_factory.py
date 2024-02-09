import os
from flask import Flask
from application.auth import Auth
from strumpatterns.strumpatterns import strumpatterns


def create_app(application_config):

    app = Flask(__name__)
    app.config.from_object(application_config)
    register_blueprints(app)

    auth = Auth()
    load_user = auth.init_app(app)

    return app


def register_blueprints(app):
    app.register_blueprint(strumpatterns, url_prefix="/")

    return app
