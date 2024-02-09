from enum import Enum

external_api_login_results = Enum(
    "login_results", ["not_found", "details_not_matched", "not_over_sixteen", "found"]
)

questionnaire_validity_states = Enum(
    "questionnaire_validity", ["not_checked", "not_valid", "valid"]
)

questionnaire_validity_messages = Enum(
    "questionnaire_validity_message",
    [
        "file not found at supplied path",
        "json could not be parsed",
        "all answers must have list of points equal to age range maximums plus one",
    ],
)
