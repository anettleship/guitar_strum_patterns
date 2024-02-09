import html
import os
import pytest
from flask import url_for, session
from flask_login import current_user, login_user
from application.config import Config
from application.app_factory import create_app
from application.auth import User
from application.config_stages import Stage
from bs4 import BeautifulSoup


def test_strumpatterns_should_exit_with_zero_length_secret_key():
    os.environ["SECRET_KEY"] = ""
    try:
        with pytest.raises(SystemExit) as error:
            app = create_app(Config(Stage.testing))
        assert error.type == SystemExit
    finally:
        os.unsetenv("SECRET_KEY")
        del(os.environ["SECRET_KEY"])

def test_strumpatterns_index_route_should_return_sucess_with_expected_html_elements():
    app = create_app(Config(Stage.testing))

    form_title = os.environ.get("GENERATOR_TITLE")

    with app.test_client() as test_client:
        response = test_client.get("/")

        soup = BeautifulSoup(response.data, "html.parser")
        assert response.status_code == 200
        assert soup.title.string == form_title
        assert soup.find(name="input", attrs={"name": "strum_pattern"})
        assert soup.find(name="button", attrs={"name": "submit"})
        assert soup.find(
            "form", {"action": url_for("strumpatterns.generate"), "method": "post"}
        )


def test_strumpatterns_should_serve_static_test_file_from_within_blueprint_static_js_folder():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/js/testfile.js")
    assert response.status_code == 200


def test_strumpatterns_login_required_route_should_redirect_to_index_when_user_not_logged_in():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/login_required")
        assert response.location == url_for('strumpatterns.login')
    assert response.status_code == 401


def test_strumpatterns_login_route_should_redirect_to_root():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/login")

        assert response.status_code == 302
        assert response.location == url_for("strumpatterns.index") 


def test_strumpatterns_generate_route_should_return_posted_form_text_in_the_rendered_page():
    app = create_app(Config(Stage.testing))

    form_data = {
        "strum_pattern": "123456789",
    }

    with app.test_client() as test_client:
        response = test_client.post("/generate", data=form_data)
        soup = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert soup.find(id="pattern_text")


def test_strumpatterns_generate_route_should_return_a_strum_pattern_image_id_in_the_rendered_page():
    app = create_app(Config(Stage.testing))

    form_data = {
        "strum_pattern": "123456789",
    }

    with app.test_client() as test_client:
        response = test_client.post("/generate", data=form_data)
        soup = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert soup.find(id="pattern_image")
