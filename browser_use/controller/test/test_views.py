import pytest
from browser_use.controller.views import NoParamsAction, SearchGoogleAction, ClickElementAction, ScrollAction

def test_no_params_action_ignores_inputs():
    """Test that NoParamsAction discards all input and always returns an empty model."""
    # Provide multiple arbitrary inputs
    instance = NoParamsAction(any_field="test", another_field=123, nested={"key": "value"})
    # The resulting model should ignore all inputs and be empty
    assert instance.dict() == {}
def test_search_google_action_initialization():
    """Test that SearchGoogleAction initializes correctly with the provided query."""
    action = SearchGoogleAction(query="example search")
    assert action.query == "example search"
def test_click_element_action_optional_xpath():
    """Test that ClickElementAction initializes correctly, with optional xpath defaulting to None if not provided."""
    # Test initialization without xpath
    action_without_xpath = ClickElementAction(index=1)
    assert action_without_xpath.xpath is None

    # Test initialization with xpath provided
    action_with_xpath = ClickElementAction(index=2, xpath="//button[@id='submit']")
    assert action_with_xpath.xpath == "//button[@id='submit']"
def test_scroll_action_initialization():
    """Test that ScrollAction initializes correctly with and without the 'amount' parameter."""
    # When no amount is provided, amount should be None
    scroll_default = ScrollAction()
    assert scroll_default.amount is None

    # When amount is provided, it should reflect the provided value
    scroll_with_amount = ScrollAction(amount=100)
    assert scroll_with_amount.amount == 100