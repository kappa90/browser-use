from unittest.mock import Mock
import pytest
from playwright.async_api import Page
from browser_use.dom.service import DomService
from browser_use.dom.views import DOMElementNode, DOMTextNode, CoordinateSet, ViewportInfo


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
        "tagName": "div",
        "xpath": "/html/body/div",
        "children": [
            {
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
    child_element = nested_node.children[0]
    assert isinstance(child_element, DOMElementNode)
    assert len(child_element.children) == 1
    child_text = child_element.children[0]
    assert isinstance(child_text, DOMTextNode)
    assert child_text.text == "Nested text"
    
    # Test handling of None input
    none_node = dom_service._parse_node(None)
    assert none_node is None
