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

    form_title = os.environ.get("LOGIN_FORM_TITLE")

    with app.test_client() as test_client:
        response = test_client.get("/")

        soup = BeautifulSoup(response.data, "html.parser")
        assert response.status_code == 200
        assert soup.title.string == form_title
        assert soup.find(name="input", attrs={"name": "first_name"})
        assert soup.find(name="input", attrs={"name": "last_name"})
        assert soup.find(name="input", attrs={"name": "date_of_birth"})
        assert soup.find(name="button", attrs={"name": "submit"})
        assert soup.find(
            "form", {"action": url_for("strumpatterns.validate"), "method": "post"}
        )


def test_strumpatterns_should_serve_static_test_file_from_within_blueprint_static_js_folder():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/js/testfile.js")
    assert response.status_code == 200


def test_strumpatterns_questionnaire_route_should_redirect_to_index_when_user_not_logged_in():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/questionnaire")
        assert response.location == url_for('strumpatterns.login')
    assert response.status_code == 401


def test_strumpatterns_calculate_score_route_should_redirect_to_index_when_user_not_logged_in():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.post("/calculate_score")
        assert response.location == url_for("strumpatterns.login")
    assert response.status_code == 401


# def test_strumpatterns_questionnaire_route_should_return_all_question_and_answer_html_elements_for_logged_in_user():
#     app = create_app(Config(Stage.testing))

#     question_form_title = os.environ.get("QUESTION_FORM_TITLE")
#     question_data_path = os.environ.get("QUESTION_DATA_PATH")
#     questionnaire_handler = QuestionnaireHandler(question_data_path)

#     with app.test_request_context("/validate_login", method="POST"):
#         with app.test_client() as test_client:
#             test_user = User("123456789")
#             login_user(test_user)
#             response = test_client.get("/questionnaire")

#             soup = BeautifulSoup(response.data, "html.parser")

#             assert soup.title.string == question_form_title

#             assert len(soup.find_all("input",{"type": "radio", "value": "Yes"})) == 3
#             assert len(soup.find_all("input",{"type": "radio", "value": "No"})) == 3

#             for question in questionnaire_handler.question_data["questions"]:
#                 assert soup.find(id=question["name"])
#                 assert (len(soup.find_all("input",{"type": "radio", "name": f"{question['name']}"})) == 2)

#             assert soup.find(name="button", attrs={"name": "submit"})
#             assert soup.find("form",{"action": url_for("strumpatterns.calculate"), "method": "post"})


def test_strumpatterns_calculate_score_route_should_return_unauthorised_when_user_not_logged_in():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.post("/calculate_score")

    assert response.status_code == 401



def test_strumpatterns_login_route_should_redirect_to_root():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/login")

        assert response.status_code == 302
        assert response.location == url_for("strumpatterns.index") 