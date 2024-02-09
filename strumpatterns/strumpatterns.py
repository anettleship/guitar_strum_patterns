import os
from flask import (
    Blueprint,
    current_app,
    send_from_directory,
    request,
    redirect,
    url_for,
    session,
)
from flask_login import login_required, login_user, logout_user
from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape
from application.auth import User

application_name = "strumpatterns"

strumpatterns = Blueprint(application_name, __name__)

jinja_env = Environment(
    loader=PackageLoader("strumpatterns"), autoescape=select_autoescape()
)


@strumpatterns.route("/")
def index():
    template = jinja_env.get_template("home.html")
    form_title = os.environ.get("LOGIN_FORM_TITLE")
    validate_url = url_for(f"{application_name}.validate")
    return template.render(title=form_title, form_action_url=validate_url)


@strumpatterns.route("/login")
def login():
    return redirect("/")


@strumpatterns.route("/js/<path:filename>")
def static_js(filename):
    return send_from_directory(f"../{application_name}/static/js", filename)


@strumpatterns.route("/generate", methods=["POST"])
def validate():
    strum_pattern = request.form["strum_pattern"]

    with current_app.app_context():
        generator = StrumPatternGenerator(strum_pattern)

    result = generator.generate()

    if not result:
        language = os.environ.get("LANGUAGE")
        title = os.environ.get("LOGIN_FORM_TITLE")
        template = jinja_env.get_template("message.html")
        return template.render(
            title=title,
            message=f"A message would be generated in the following language: {language}."
        )

    template = jinja_env.get_template("pattern.html")
    pattern_title = os.environ.get("PATTERN_TITLE")
    return template.render(
        title=pattern_title,
        image=result,
    )


@strumpatterns.route("/login_required")
@login_required
def login_required():
    return "logged in"
