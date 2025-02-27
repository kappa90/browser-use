import pytest
from browser_use.controller.views import NoParamsAction, SwitchTabAction, ClickElementAction, InputTextAction

def test_no_params_action_ignores_input():
    """Test that NoParamsAction ignores any input data and returns an empty model."""
    # Provide some input that NoParamsAction should ignore.
    input_data = {"unexpected_field": "some value", "another_field": 123, "nested": {"key": "value"}}
    # Parse the input data with NoParamsAction.
    model = NoParamsAction.parse_obj(input_data)
    # Assert that the model's dict is empty.
    assert model.dict() == {}
def test_switch_tab_action_valid_input():
    """Test that SwitchTabAction properly parses valid input and coerces types correctly."""
    # Test with an integer for page_id
    input_data_int = {"page_id": 5}
    model_int = SwitchTabAction.parse_obj(input_data_int)
    assert model_int.page_id == 5
    assert model_int.dict() == {"page_id": 5}

    # Test with a string that represents an integer for page_id to check type coercion.
    input_data_str = {"page_id": "10"}
    model_str = SwitchTabAction.parse_obj(input_data_str)
    assert model_str.page_id == 10
    assert model_str.dict() == {"page_id": 10}
def test_click_element_action_optional_xpath():
    """Test that ClickElementAction properly handles the optional xpath parameter."""
    # Test with index only, xpath should default to None.
    input_data_no_xpath = {"index": 1}
    model_no_xpath = ClickElementAction.parse_obj(input_data_no_xpath)
    assert model_no_xpath.index == 1
    assert model_no_xpath.xpath is None

    # Test with index and xpath provided.
    input_data_with_xpath = {"index": 2, "xpath": "//div[@class='example']"}
    model_with_xpath = ClickElementAction.parse_obj(input_data_with_xpath)
    assert model_with_xpath.index == 2
    assert model_with_xpath.xpath == "//div[@class='example']"
def test_input_text_action():
    """Test that InputTextAction properly parses valid input, coerces types, and handles the optional xpath parameter."""
    # Test with index provided as string and without xpath (xpath should default to None)
    input_data_no_xpath = {"index": "3", "text": "hello"}
    model_no_xpath = InputTextAction.parse_obj(input_data_no_xpath)
    assert model_no_xpath.index == 3
    assert model_no_xpath.text == "hello"
    assert model_no_xpath.xpath is None

    # Test with both index and xpath provided, and index as a string to check type coercion
    input_data_with_xpath = {"index": "4", "text": "world", "xpath": "//span[@id='token']"}
    model_with_xpath = InputTextAction.parse_obj(input_data_with_xpath)
    assert model_with_xpath.index == 4
    assert model_with_xpath.text == "world"
    assert model_with_xpath.xpath == "//span[@id='token']"