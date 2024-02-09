from strumpatterns.strum_pattern_generator import StrumPatternGenerator


def test_strum_pattern_generator_generate_method_returns_string_passed_as_parameter():
    input_string = "input_string"
    strum_pattern_generator = StrumPatternGenerator(input_string)

    result = strum_pattern_generator.generate()

    assert result == input_string
