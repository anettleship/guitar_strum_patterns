from strumpatterns.strum_pattern_generator import StrumPatternGenerator


def test_strum_pattern_generator_generate_should_return_base64_encoded_png_data():
    input_string = "input_string"
    strum_pattern_generator = StrumPatternGenerator(input_string)

    result = strum_pattern_generator.generate()
    
    # iVBORw0KGg - https://stackoverflow.com/questions/62329321/how-can-i-check-a-base64-string-is-a-filewhat-type-or-not/62330081#62330081
    assert result.startswith("iVBORw0KGg")
