"""
Utility functions for the Shortcut MCP Server.

This module contains helper functions for common tasks.
"""

from typing import Dict, List, Any, Optional

def format_story_for_display(story: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a story object for display in the MCP.

    Args:
        story: Story object from Shortcut API

    Returns:
        Formatted story with selected fields
    """
    return {
        "id": story.get("id"),
        "name": story.get("name"),
        "type": story.get("story_type"),
        "state": story.get("workflow_state_name", ""),
        "owner": get_owner_name(story),
        "url": story.get("app_url", ""),
        "estimate": story.get("estimate"),
        "created_at": story.get("created_at"),
        "updated_at": story.get("updated_at"),
    }


def get_owner_name(story: Dict[str, Any]) -> str:
    """
    Extract the owner name from a story.

    Args:
        story: Story object from Shortcut API

    Returns:
        Owner name or empty string if no owner
    """
    owner = None
    owners = story.get("owner_ids", [])
    
    if owners and len(owners) > 0:
        # In a real implementation, you'd want to look up the actual name
        # from the member ID using the members endpoint
        return f"Owner ID: {owners[0]}"
    
    return ""


def format_search_results(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format a list of stories for display in search results.

    Args:
        stories: List of story objects from Shortcut API

    Returns:
        List of formatted stories
    """
    return [format_story_for_display(story) for story in stories]


def build_error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """
    Build a standardized error response.

    Args:
        message: Error message
        status_code: HTTP status code

    Returns:
        Error response dictionary
    """
    return {
        "error": True,
        "message": message,
        "status_code": status_code
    }
