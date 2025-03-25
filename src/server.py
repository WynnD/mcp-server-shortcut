"""
MCP Server for Shortcut.com integration.

This server provides an interface for accessing and searching Shortcut tickets using the
Model Context Protocol (MCP).

Run this server with:
python -m src.server
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Literal

from mcp.server.fastmcp import FastMCP

from .shortcut_client import ShortcutClient
from .utils import (
    StoryType, 
    StorySummary, 
    StoryDetail, 
    Comment, 
    WorkflowState,
    Project, 
    ErrorResponse, 
    SuccessResponse,
    create_bug_report_template,
    create_feature_request_template
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the Shortcut client
shortcut_client = ShortcutClient()

# Initialize FastMCP server with dependencies
mcp = FastMCP(
    "Shortcut.com Ticket Manager",
    dependencies=[
        "requests",
        "httpx",
        "pydantic",
        "python-dotenv"
    ]
)

# Resource implementations
@mcp.resource("shortcut://stories?workflow_state_id={workflow_state_id}&project_id={project_id}&limit={limit}")
async def get_stories_resource(
    workflow_state_id: Optional[int] = None,
    project_id: Optional[int] = None,
    limit: int = 20
) -> str:
    """
    Access stories from Shortcut as a resource
    
    Args:
        workflow_state_id: Filter by workflow state ID
        project_id: Filter by project ID
        limit: Maximum number of stories to return
    """
    params = {}
    if workflow_state_id:
        params["workflow_state_id"] = workflow_state_id
    if project_id:
        params["project_id"] = project_id
    
    stories = await shortcut_client.get_stories_async(params)
    
    # Limit the results
    stories = stories[:limit] if limit > 0 else stories
    
    try:
        # Convert raw stories to validated model objects
        formatted_stories = [StorySummary.model_validate(story).model_dump() for story in stories]
        return json.dumps(formatted_stories, indent=2)
    except Exception as e:
        logger.error(f"Error formatting stories: {e}")
        return json.dumps({"error": f"Error formatting stories: {str(e)}"})

@mcp.resource("shortcut://story/{story_id}")
async def get_story_resource(story_id: int) -> str:
    """
    Access a specific story from Shortcut as a resource
    
    Args:
        story_id: ID of the story to retrieve
    """
    story = await shortcut_client.get_story_by_id_async(story_id)
    
    if not story:
        return json.dumps({"error": f"Story with ID {story_id} not found"})
    
    try:
        # Convert raw story to validated model object
        formatted_story = StoryDetail.model_validate(story).model_dump()
        return json.dumps(formatted_story, indent=2)
    except Exception as e:
        logger.error(f"Error formatting story: {e}")
        return json.dumps({"error": f"Error formatting story: {str(e)}"})

# Tool implementations
@mcp.tool()
async def list_stories(
    workflow_state_id: Optional[int] = None,
    project_id: Optional[int] = None,
    owner_id: Optional[str] = None,
    limit: int = 25
) -> str:
    """
    List stories from Shortcut with optional filtering.
    
    Args:
        workflow_state_id: Filter by workflow state ID
        project_id: Filter by project ID
        owner_id: Filter by owner user ID
        limit: Maximum number of stories to return (default: 25)
        
    Returns:
        Formatted list of stories
    """
    params = {}
    if workflow_state_id:
        params["workflow_state_id"] = workflow_state_id
    if project_id:
        params["project_id"] = project_id
    if owner_id:
        params["owner_ids[]"] = owner_id
    
    stories = await shortcut_client.get_stories_async(params)
    
    # Limit the results
    stories = stories[:limit] if limit > 0 else stories
    
    try:
        # Convert raw stories to validated model objects
        formatted_stories = [StorySummary.model_validate(story).model_dump() for story in stories]
        return json.dumps(formatted_stories, indent=2)
    except Exception as e:
        logger.error(f"Error formatting stories: {e}")
        return json.dumps({"error": f"Error formatting stories: {str(e)}"})

@mcp.tool()
async def search_stories(query: str, limit: int = 25) -> str:
    """
    Search for stories in Shortcut.
    
    Args:
        query: Search query string
        limit: Maximum number of stories to return (default: 25)
        
    Returns:
        Formatted search results
    """
    if not query:
        return json.dumps({"error": "Search query is required"})
    
    stories = await shortcut_client.search_stories_async(query, limit)
    
    try:
        # Convert raw stories to validated model objects
        formatted_stories = [StorySummary.model_validate(story).model_dump() for story in stories]
        return json.dumps(formatted_stories, indent=2)
    except Exception as e:
        logger.error(f"Error formatting search results: {e}")
        return json.dumps({"error": f"Error formatting search results: {str(e)}"})

@mcp.tool()
async def get_story_details(story_id: int) -> str:
    """
    Get detailed information about a specific story.
    
    Args:
        story_id: The ID of the story to retrieve
        
    Returns:
        Formatted story details
    """
    story = await shortcut_client.get_story_by_id_async(story_id)
    
    if not story:
        return json.dumps({"error": f"Story with ID {story_id} not found"})
    
    try:
        # Convert raw story to validated model object
        formatted_story = StoryDetail.model_validate(story).model_dump()
        return json.dumps(formatted_story, indent=2)
    except Exception as e:
        logger.error(f"Error formatting story: {e}")
        return json.dumps({"error": f"Error formatting story: {str(e)}"})

@mcp.tool()
async def create_story(
    name: str,
    description: str,
    story_type: StoryType = StoryType.FEATURE,
    project_id: Optional[int] = None,
    workflow_state_id: Optional[int] = None,
    owner_ids: Optional[List[str]] = None,
    labels: Optional[List[str]] = None
) -> str:
    """
    Create a new story in Shortcut.
    
    Args:
        name: The name/title of the story
        description: The description of the story
        story_type: Type of story (feature, bug, chore)
        project_id: ID of the project to assign the story to
        workflow_state_id: ID of the workflow state
        owner_ids: List of user IDs to assign as owners
        labels: List of label names to add to the story
        
    Returns:
        Formatted created story details
    """
    # Prepare the story data
    story_data = {
        "name": name,
        "description": description,
        "story_type": story_type if isinstance(story_type, str) else story_type.value
    }
    
    if project_id:
        story_data["project_id"] = project_id
    
    if workflow_state_id:
        story_data["workflow_state_id"] = workflow_state_id
    
    if owner_ids:
        story_data["owner_ids"] = owner_ids
        
    if labels:
        story_data["labels"] = [{"name": label} for label in labels]
    
    # Create the story
    created_story = await shortcut_client.create_story_async(story_data)
    
    if not created_story:
        return json.dumps({"error": "Failed to create story"})
    
    try:
        # Convert raw created story to validated model object
        formatted_story = StoryDetail.model_validate(created_story).model_dump()
        return json.dumps(formatted_story, indent=2)
    except Exception as e:
        logger.error(f"Error formatting created story: {e}")
        return json.dumps({"error": f"Error formatting created story: {str(e)}"})

@mcp.tool()
async def update_story(
    story_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    story_type: Optional[StoryType] = None,
    workflow_state_id: Optional[int] = None,
    owner_ids: Optional[List[str]] = None
) -> str:
    """
    Update an existing story in Shortcut.
    
    Args:
        story_id: ID of the story to update
        name: New name/title for the story
        description: New description for the story
        story_type: New type for the story
        workflow_state_id: New workflow state ID
        owner_ids: New list of owner user IDs
        
    Returns:
        Formatted updated story details
    """
    # Prepare the update data
    update_data = {}
    
    if name:
        update_data["name"] = name
        
    if description:
        update_data["description"] = description
        
    if story_type:
        update_data["story_type"] = story_type if isinstance(story_type, str) else story_type.value
        
    if workflow_state_id:
        update_data["workflow_state_id"] = workflow_state_id
        
    if owner_ids:
        update_data["owner_ids"] = owner_ids
    
    # Update the story
    updated_story = await shortcut_client.update_story_async(story_id, update_data)
    
    if not updated_story:
        return json.dumps({"error": f"Failed to update story {story_id}"})
    
    try:
        # Convert raw updated story to validated model object
        formatted_story = StoryDetail.model_validate(updated_story).model_dump()
        return json.dumps(formatted_story, indent=2)
    except Exception as e:
        logger.error(f"Error formatting updated story: {e}")
        return json.dumps({"error": f"Error formatting updated story: {str(e)}"})

@mcp.tool()
async def add_comment(story_id: int, text: str) -> str:
    """
    Add a comment to a story in Shortcut.
    
    Args:
        story_id: ID of the story to comment on
        text: Comment text
        
    Returns:
        Status of the comment creation
    """
    comment = await shortcut_client.add_comment_async(story_id, text)
    
    if not comment:
        return json.dumps({"error": f"Failed to add comment to story {story_id}"})
    
    try:
        # Create validated response
        success_response = SuccessResponse(
            success=True,
            message="Comment added successfully",
            data=Comment.model_validate(comment).model_dump()
        ).model_dump()
        
        return json.dumps(success_response, indent=2)
    except Exception as e:
        logger.error(f"Error formatting comment response: {e}")
        return json.dumps({"error": f"Error formatting comment response: {str(e)}"})

@mcp.tool()
async def list_workflow_states() -> str:
    """
    List all workflow states in the Shortcut workspace.
    
    Returns:
        Formatted list of workflow states
    """
    workflows = await shortcut_client.get_workflow_states_async()
    
    try:
        # Extract workflow states from all workflows
        all_states = []
        for workflow in workflows:
            for state in workflow.get("states", []):
                all_states.append(WorkflowState(
                    id=state.get("id"),
                    name=state.get("name"),
                    type=state.get("type"),
                    workflow_id=workflow.get("id"),
                    workflow_name=workflow.get("name")
                ).model_dump())
        
        return json.dumps(all_states, indent=2)
    except Exception as e:
        logger.error(f"Error formatting workflow states: {e}")
        return json.dumps({"error": f"Error formatting workflow states: {str(e)}"})

@mcp.tool()
async def list_projects() -> str:
    """
    List all projects in the Shortcut workspace.
    
    Returns:
        Formatted list of projects
    """
    projects = await shortcut_client.get_projects_async()
    
    try:
        # Format projects for display
        formatted_projects = [Project(
            id=project.get("id"),
            name=project.get("name"),
            description=project.get("description"),
            archived=project.get("archived", False)
        ).model_dump() for project in projects]
        
        return json.dumps(formatted_projects, indent=2)
    except Exception as e:
        logger.error(f"Error formatting projects: {e}")
        return json.dumps({"error": f"Error formatting projects: {str(e)}"})

# Prompt templates
@mcp.prompt()
def create_bug_report(title: str, steps: str, expected: str, actual: str) -> str:
    """
    Create a bug report template
    
    Args:
        title: Bug title
        steps: Steps to reproduce
        expected: Expected behavior
        actual: Actual behavior
    """
    return create_bug_report_template(title, steps, expected, actual)

@mcp.prompt()
def create_feature_request(title: str, description: str, user_value: str, acceptance_criteria: str) -> str:
    """
    Create a feature request template
    
    Args:
        title: Feature title
        description: Description of the feature
        user_value: Value to users
        acceptance_criteria: Acceptance criteria
    """
    return create_feature_request_template(title, description, user_value, acceptance_criteria)

def main():
    """Main entry point for the server"""
    mcp.run()

# Run the server
if __name__ == "__main__":
    main()
