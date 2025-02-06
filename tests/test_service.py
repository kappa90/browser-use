from unittest.mock import Mock
from playwright.async_api import Page
from browser_use.dom.service import DomService
from browser_use.dom.views import DOMElementNode, DOMTextNode


def test_parse_node():
    """
    Test the _parse_node method of DomService to ensure it correctly parses a simple DOM structure.
    This test checks if:
    1. The method correctly creates a DOMElementNode for an element.
    2. The method correctly creates a DOMTextNode for text content.
    3. The parent-child relationships are properly established.
    4. The attributes are correctly assigned to the DOMElementNode.
    """
    # Create a mock Page object
    mock_page = Mock(spec=Page)
    
    # Create a DomService instance
    dom_service = DomService(mock_page)
    
    # Create a sample node_data dictionary representing a simple DOM structure
    node_data = {
        "type": "ELEMENT_NODE",
        "tagName": "div",
        "xpath": "/html/body/div",
        "attributes": {"class": "container"},
        "isVisible": True,
        "isInteractive": False,
        "isTopElement": True,
        "children": [
            {
                "type": "TEXT_NODE",
                "text": "Hello, World!",
                "isVisible": True
            }
        ]
    }
    
    # Parse the node_data
    parsed_node = dom_service._parse_node(node_data)
    
    # Assertions
    assert isinstance(parsed_node, DOMElementNode)
    assert parsed_node.tag_name == "div"
    assert parsed_node.xpath == "/html/body/div"
    assert parsed_node.attributes == {"class": "container"}
    assert parsed_node.is_visible is True
    assert parsed_node.is_interactive is False
    assert parsed_node.is_top_element is True
    
    assert len(parsed_node.children) == 1
    child_node = parsed_node.children[0]
    assert isinstance(child_node, DOMTextNode)
    assert child_node.text == "Hello, World!"
    assert child_node.is_visible is True
    assert child_node.parent == parsed_node
