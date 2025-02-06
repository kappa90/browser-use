import os
import sys
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from playwright.async_api import Page
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel

from browser_use.agent.message_manager.service import MessageManager
from browser_use.agent.service import Agent
from browser_use.agent.views import ActionResult, AgentOutput
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContext
from browser_use.browser.views import BrowserState
from browser_use.controller.registry.service import Registry
from browser_use.controller.registry.views import ActionModel
from browser_use.controller.service import Controller

from browser_use.dom.service import DomService
from browser_use.dom.views import DOMTextNode, DOMElementNode, CoordinateSet, ViewportInfo


# ----------------- Agent and Registry Tests -----------------

class TestAgent:
    @pytest.fixture
    def mock_controller(self):
        controller = Mock(spec=Controller)
        registry = Mock(spec=Registry)
        registry.registry = MagicMock()
        registry.registry.actions = {'test_action': MagicMock(param_model=MagicMock())}  # type: ignore
        controller.registry = registry
        return controller

    @pytest.fixture
    def mock_llm(self):
        return Mock(spec=BaseChatModel)

    @pytest.fixture
    def mock_browser(self):
        return Mock(spec=Browser)

    @pytest.fixture
    def mock_browser_context(self):
        return Mock(spec=BrowserContext)

    def test_convert_initial_actions(self, mock_controller, mock_llm, mock_browser, mock_browser_context):  # type: ignore
        """
        Test that the _convert_initial_actions method correctly converts
        dictionary-based actions to ActionModel instances.
        """
        # Arrange
        agent = Agent(
            task='Test task', llm=mock_llm, controller=mock_controller,
            browser=mock_browser, browser_context=mock_browser_context
        )
        initial_actions = [{'test_action': {'param1': 'value1', 'param2': 'value2'}}]

        # Mock the ActionModel
        mock_action_model = MagicMock(spec=ActionModel)
        mock_action_model_instance = MagicMock()
        mock_action_model.return_value = mock_action_model_instance
        agent.ActionModel = mock_action_model  # type: ignore

        # Act
        result = agent._convert_initial_actions(initial_actions)

        # Assert
        assert len(result) == 1
        mock_controller.registry.registry.actions['test_action'].param_model.assert_called_once_with(  # type: ignore
            param1='value1', param2='value2'
        )
        mock_action_model.assert_called_once()
        assert isinstance(result[0], MagicMock)
        assert result[0] == mock_action_model_instance

        # Check that the ActionModel was called with the correct parameters
        call_args = mock_action_model.call_args[1]
        assert 'test_action' in call_args
        assert call_args['test_action'] == mock_controller.registry.registry.actions['test_action'].param_model.return_value  # type: ignore

    @pytest.mark.asyncio
    async def test_step_error_handling(self):
        """
        Test the error handling in the step method of the Agent class.
        This test simulates a failure in the get_next_action method and
        checks if the error is properly handled and recorded.
        """
        # Mock the LLM
        mock_llm = MagicMock(spec=BaseChatModel)

        # Mock the MessageManager
        with patch('browser_use.agent.service.MessageManager') as mock_message_manager:
            # Create an Agent instance with mocked dependencies
            agent = Agent(task='Test task', llm=mock_llm)

            # Mock the get_next_action method to raise an exception
            agent.get_next_action = AsyncMock(side_effect=ValueError('Test error'))

            # Mock the browser_context
            agent.browser_context = AsyncMock()
            agent.browser_context.get_state = AsyncMock(
                return_value=BrowserState(
                    url='https://example.com',
                    title='Example',
                    element_tree=MagicMock(),  # Mocked element tree
                    tabs=[],
                    selector_map={},
                    screenshot='',
                )
            )

            # Mock the controller
            agent.controller = AsyncMock()

            # Call the step method
            await agent.step()

            # Assert that the error was handled and recorded
            assert agent.consecutive_failures == 1
            assert len(agent._last_result) == 1
            assert isinstance(agent._last_result[0], ActionResult)
            assert 'Test error' in agent._last_result[0].error
            assert agent._last_result[0].include_in_memory is True


class TestRegistry:
    @pytest.fixture
    def registry_with_excludes(self):
        return Registry(exclude_actions=['excluded_action'])

    def test_action_decorator_with_excluded_action(self, registry_with_excludes):
        """
        Test that the action decorator does not register an action
        if it's in the exclude_actions list.
        """

        # Define a function to be decorated
        def excluded_action():
            pass

        # Apply the action decorator
        decorated_func = registry_with_excludes.action(description='This should be excluded')(excluded_action)

        # Assert that the decorated function is the same as the original
        assert decorated_func == excluded_action

        # Assert that the action was not added to the registry
        assert 'excluded_action' not in registry_with_excludes.registry.actions

        # Define another function that should be included
        def included_action():
            pass

        # Apply the action decorator to an included action
        registry_with_excludes.action(description='This should be included')(included_action)

        # Assert that the included action was added to the registry
        assert 'included_action' in registry_with_excludes.registry.actions


# ----------------- DomService Tests -----------------

@pytest.mark.asyncio
async def test_parse_node():
    """
    Test the _parse_node method of DomService to ensure it correctly parses
    different types of nodes and creates the expected DOM structure.
    
    This test covers:
    1. Parsing a text node
    2. Parsing an element node with attributes, coordinates, and viewport info
    3. Parsing a nested structure with both element and text nodes
    4. Handling of None input
    """
    # Create a mock Page object
    mock_page = Mock(spec=Page)
    
    # Initialize DomService with the mock Page
    dom_service = DomService(mock_page)
    
    # Test parsing a text node
    text_node_data = {
        "type": "TEXT_NODE",
        "text": "Hello, world!",
        "isVisible": True
    }
    text_node = dom_service._parse_node(text_node_data)
    assert isinstance(text_node, DOMTextNode)
    assert text_node.text == "Hello, world!"
    assert text_node.is_visible is True
    
    # Test parsing an element node with attributes and coordinates
    element_node_data = {
        "type": "ELEMENT_NODE",
        "tagName": "div",
        "xpath": "/html/body/div",
        "attributes": {"class": "container"},
        "isVisible": True,
        "isInteractive": False,
        "isTopElement": True,
        "highlightIndex": 1,
        "viewportCoordinates": {
            "topLeft": {"x": 0, "y": 0},
            "topRight": {"x": 100, "y": 0},
            "bottomLeft": {"x": 0, "y": 50},
            "bottomRight": {"x": 100, "y": 50},
            "center": {"x": 50, "y": 25},
            "width": 100,
            "height": 50
        },
        "pageCoordinates": {
            "topLeft": {"x": 0, "y": 0},
            "topRight": {"x": 100, "y": 0},
            "bottomLeft": {"x": 0, "y": 50},
            "bottomRight": {"x": 100, "y": 50},
            "center": {"x": 50, "y": 25},
            "width": 100,
            "height": 50
        },
        "viewport": {
            "scrollX": 0,
            "scrollY": 0,
            "width": 1024,
            "height": 768
        },
        "children": []
    }
    element_node = dom_service._parse_node(element_node_data)
    assert isinstance(element_node, DOMElementNode)
    assert element_node.tag_name == "div"
    assert element_node.xpath == "/html/body/div"
    assert element_node.attributes == {"class": "container"}
    assert element_node.is_visible is True
    assert element_node.is_interactive is False
    assert element_node.is_top_element is True
    assert element_node.highlight_index == 1
    assert isinstance(element_node.viewport_coordinates, CoordinateSet)
    assert isinstance(element_node.page_coordinates, CoordinateSet)
    assert isinstance(element_node.viewport_info, ViewportInfo)
    
    # Test parsing a nested structure
    nested_node_data = {
        "type": "ELEMENT_NODE",
        "tagName": "div",
        "xpath": "/html/body/div",
        "children": [
            {
                "type": "ELEMENT_NODE",
                "tagName": "p",
                "xpath": "/html/body/div/p",
                "children": [
                    {
                        "type": "TEXT_NODE",
                        "text": "Nested text",
                        "isVisible": True
                    }
                ]
            }
        ]
    }
    nested_node = dom_service._parse_node(nested_node_data)
    assert isinstance(nested_node, DOMElementNode)
    assert len(nested_node.children) == 1
    assert isinstance(nested_node.children[0], DOMElementNode)
    assert len(nested_node.children[0].children) == 1
    assert isinstance(nested_node.children[0].children[0], DOMTextNode)
    assert nested_node.children[0].children[0].text == "Nested text"
    
    # Test handling of None input
    none_node = dom_service._parse_node(None)
    assert none_node is None
