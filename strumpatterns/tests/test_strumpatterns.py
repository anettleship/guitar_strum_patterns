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


@pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"]))
def test_strumpatterns_validate_route_should_return_success_from_post_request():
    app = create_app(Config(Stage.testing))

    form_data = {
        "nhs_number": "123456789",
        "first_name": "Kent",
        "last_name": "Beck",
        "date_of_birth": "1961-03-31",
    }

    with app.test_client() as test_client:
        response = test_client.post("/validate_login", data=form_data)
    assert response.status_code == 200


@pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"]))
def test_strumpatterns_validate_route_should_return_not_found_message_for_invalid_user():
    app = create_app(Config(Stage.testing))

    form_data = {
        "nhs_number": "123456789",
        "first_name": "Kent",
        "last_name": "Beck",
        "date_of_birth": "1961-03-31",
    }

    expected_message = "Your details could not be found"

    with app.test_client() as test_client:
        response = test_client.post("/validate_login", data=form_data)
    soup = BeautifulSoup(response.data, "html.parser")

    assert len(soup.find_all(string=expected_message)) == 1


@pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"]))
def test_strumpatterns_validate_route_should_return_not_found_for_details_not_matched():
    app = create_app(Config(Stage.testing))

    form_data = {
        "nhs_number": "111222333",
        "first_name": "Kent",
        "last_name": "Beck",
        "date_of_birth": "31-03-1961",
    }

    expected_message = "Your details could not be found"

    with app.test_client() as test_client:
        response = test_client.post("/validate_login", data=form_data)
    soup = BeautifulSoup(response.data, "html.parser")

    assert len(soup.find_all(string=expected_message)) == 1


@pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"]))
def test_strumpatterns_validate_route_should_return_not_over_sixteen_for_under_sixteens():
    app = create_app(Config(Stage.testing))

    form_data = {
        "nhs_number": "555666777",
        "first_name": "Megan",
        "last_name": "May",
        "date_of_birth": "2008-11-14",
    }

    expected_message = "You are not eligible for this service"

    with app.test_client() as test_client:
        response = test_client.post("/validate_login", data=form_data)
    soup = BeautifulSoup(response.data, "html.parser")

    assert len(soup.find_all(string=expected_message)) == 1


@pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"]))
def test_strumpatterns_validate_route_should_log_user_in_when_details_match():
    app = create_app(Config(Stage.testing))

    form_data = {
        "nhs_number": "444555666",
        "first_name": "Charles",
        "last_name": "Bond",
        "date_of_birth": "1952-07-18",
    }

    with app.test_client() as test_client:
        response = test_client.post("/validate_login", data=form_data)
        assert current_user.is_authenticated


@pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"]))
def test_strumpatterns_validate_route_should_set_current_user_id_with_obfuscated_nhs_number():
    app = create_app(Config(Stage.testing))

    form_data = {
        "nhs_number": "444555666",
        "first_name": "Charles",
        "last_name": "Bond",
        "date_of_birth": "1952-07-18",
    }

    with app.test_client() as test_client:
        test_client.post("/validate_login", data=form_data)
        assert current_user.id == obfuscate_string_base64(form_data["nhs_number"])


@pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"]))
def test_strumpatterns_validate_route_should_set_session_with_user_age():
    app = create_app(Config(Stage.testing))

    form_data = {
        "nhs_number": "444555666",
        "first_name": "Charles",
        "last_name": "Bond",
        "date_of_birth": "1952-07-18",
    }

    with app.test_client() as test_client:
        response = test_client.post("/validate_login", data=form_data)
        assert session["user_age"] == 70


def test_strumpatterns_questionnaire_route_should_redirect_to_index_when_user_not_logged_in():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/questionnaire")
        assert response.location == url_for('strumpatterns.login')
    assert response.status_code == 401


def test_strumpatterns_questionnaire_route_should_return_sucesss_for_logged_in_user():
    app = create_app(Config(Stage.testing))

    with app.test_request_context("/questionnaire", method="GET"):
        with app.test_client() as test_client:
            test_user = User("123456789")
            login_user(test_user)
            response = test_client.get("/questionnaire")

            assert response.status_code == 200


def test_strumpatterns_calculate_score_route_should_redirect_to_index_when_user_not_logged_in():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.post("/calculate_score")
        assert response.location == url_for("strumpatterns.login")
    assert response.status_code == 401


def test_strumpatterns_questionnaire_route_should_return_all_question_and_answer_html_elements_for_logged_in_user():
    app = create_app(Config(Stage.testing))

    question_form_title = os.environ.get("QUESTION_FORM_TITLE")
    question_data_path = os.environ.get("QUESTION_DATA_PATH")
    questionnaire_handler = QuestionnaireHandler(question_data_path)

    with app.test_request_context("/validate_login", method="POST"):
        with app.test_client() as test_client:
            test_user = User("123456789")
            login_user(test_user)
            response = test_client.get("/questionnaire")

            soup = BeautifulSoup(response.data, "html.parser")

            assert soup.title.string == question_form_title

            assert len(soup.find_all("input",{"type": "radio", "value": "Yes"})) == 3
            assert len(soup.find_all("input",{"type": "radio", "value": "No"})) == 3

            for question in questionnaire_handler.question_data["questions"]:
                assert soup.find(id=question["name"])
                assert (len(soup.find_all("input",{"type": "radio", "name": f"{question['name']}"})) == 2)

            assert soup.find(name="button", attrs={"name": "submit"})
            assert soup.find("form",{"action": url_for("strumpatterns.calculate"), "method": "post"})


def test_strumpatterns_calculate_score_route_should_return_success_from_post_request_for_logged_in_user_with_age_set_in_session():
    app = create_app(Config(Stage.testing))

    with app.test_request_context("/validate_login", method="POST"):
        with app.test_client() as test_client:
            with test_client.session_transaction() as session:
                session["user_age"] = 16
            test_user = User("123456789")
            login_user(test_user)
            response = test_client.post("/calculate_score")

    assert response.status_code == 200


def test_strumpatterns_calculate_score_route_should_return_unauthorised_when_user_not_logged_in():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.post("/calculate_score")

    assert response.status_code == 401


known_questionnaire_result_for_age_and_answers = [
    (16, ["No", "No", "Yes"], 0, "great_work"),
    (66, ["No", "No", "Yes"], 0, "great_work"),
    (16, ["Yes", "No", "Yes"], 1, "great_work"),
    (16, ["Yes", "Yes", "Yes"], 3, "great_work"),
    (16, ["Yes", "Yes", "No"], 4, "please_call"),
    (21, ["Yes", "Yes", "No"], 4, "please_call"),
    (22, ["Yes", "Yes", "No"], 7, "please_call"),
    (40, ["Yes", "Yes", "No"], 7, "please_call"),
    (41, ["No", "No", "No"], 2, "great_work"),
    (65, ["No", "No", "No"], 1, "great_work"),
    (65, ["Yes", "Yes", "No"], 7, "please_call"),
    (85, ["No", "No", "No"], 1, "great_work"),
]


@pytest.mark.parametrize(
    "age,answers,score,expected", known_questionnaire_result_for_age_and_answers
)
def test_strumpatterns_calculate_score_route_should_return_correct_message_for_given_test_user_ages_and_answers_with_logged_in_user_and_age_set_in_seesion(
    age, answers, score, expected
):
    app = create_app(Config(Stage.testing))
    question_data_path = os.environ.get("QUESTION_DATA_PATH")
    questionnaire_handler = QuestionnaireHandler(question_data_path)
    form_data = {
        "Q1": f"{answers[0]}",
        "Q2": f"{answers[1]}",
        "Q3": f"{answers[2]}",
        "Submit": "",
    }

    language = "en-gb"

    with app.test_request_context("/validate_login", method="POST"):
        with app.test_client() as test_client:
            with test_client.session_transaction() as session:
                session["user_age"] = age
            test_user = User("123456789")
            login_user(test_user)
            response = test_client.post("/calculate_score", data=form_data)

    expected_message = questionnaire_handler.question_data["messages"][language][expected]
    soup = BeautifulSoup(response.data, "html.parser")

    assert len(soup.find_all(string=expected_message)) == 1


def test_strumpatterns_calculate_score_route_should_log_user_out_after_returning_message():
    app = create_app(Config(Stage.testing))
    form_data = {
        "Q1": "Yes",
        "Q2": "Yes",
        "Q3": "Yes",
        "Submit": "",
    }

    with app.test_request_context("/validate_login", method="POST"):
        with app.test_client() as test_client:
            with test_client.session_transaction() as session:
                session["user_age"] = 70
            test_user = User("123456789")
            login_user(test_user)
            test_client.post("/calculate_score", data=form_data)

            assert not current_user.is_authenticated


def test_strumpatterns_login_route_should_redirect_to_root():
    app = create_app(Config(Stage.testing))

    with app.test_client() as test_client:
        response = test_client.get("/login")

        assert response.status_code == 302
        assert response.location == url_for("strumpatterns.index") 