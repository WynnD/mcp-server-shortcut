"""
Utility functions for the Shortcut MCP Server.

This module contains helper functions and data models for common tasks.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Literal, Union
from enum import Enum

from pydantic import BaseModel, Field, validator

# Define Pydantic models for type safety and validation
# Change from Enum to Literal to avoid $ref generation
StoryType = Literal["feature", "bug", "chore"]

# Comment out the old enum class
# class StoryType(str, Enum):
#     """Enumeration of story types in Shortcut."""
#     FEATURE = "feature"
#     BUG = "bug"
#     CHORE = "chore"
    
class StorySummary(BaseModel):
    """Model for summarized story information."""
    id: int
    name: str
    story_type: Optional[StoryType] = None
    workflow_state_id: Optional[int] = None
    workflow_state_name: Optional[str] = None
    estimate: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        use_enum_values = True

class Comment(BaseModel):
    """Model for story comments."""
    id: Optional[int] = None
    text: str
    author_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class StoryDetail(BaseModel):
    """Model for detailed story information."""
    id: int
    name: str
    description: Optional[str] = None
    story_type: Optional[StoryType] = None
    workflow_state_id: Optional[int] = None
    workflow_state_name: Optional[str] = None
    estimate: Optional[int] = None
    project_id: Optional[int] = None
    owner_ids: List[str] = Field(default_factory=list)
    label_ids: List[int] = Field(default_factory=list) 
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deadline: Optional[str] = None
    comments: List[Dict] = Field(default_factory=list)
    external_links: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True

class WorkflowState(BaseModel):
    """Model for workflow state information."""
    id: int
    name: str
    type: str
    workflow_id: int
    workflow_name: str

class Project(BaseModel):
    """Model for project information."""
    id: int
    name: str
    description: Optional[str] = None
    archived: bool = False

class ErrorResponse(BaseModel):
    """Model for standardized error responses."""
    error: str
    details: Optional[Dict] = None

class SuccessResponse(BaseModel):
    """Model for standardized success responses."""
    success: bool = True
    message: str
    data: Optional[Any] = None


def format_story_for_display(story: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a story object for display in the MCP.

    Args:
        story: Story object from Shortcut API

    Returns:
        Formatted story with selected fields
    """
    try:
        # Convert raw story to validated model object with proper type checking
        story_detail = StoryDetail(
            id=story.get("id") or 0,  # Provide default for required field
            name=story.get("name") or "",  # Provide default for required field
            description=story.get("description"),
            story_type=story.get("story_type"),
            workflow_state_id=story.get("workflow_state_id"),
            workflow_state_name=story.get("workflow_state_name"),
            estimate=story.get("estimate"),
            project_id=story.get("project_id"),
            owner_ids=story.get("owner_ids", []),
            label_ids=story.get("label_ids", []),
            created_at=story.get("created_at"),
            updated_at=story.get("updated_at"),
            deadline=story.get("deadline"),
            comments=story.get("comments", []),
            external_links=story.get("external_links", [])
        )
        return story_detail.model_dump()
    except Exception as e:
        # Fallback to basic formatting if validation fails
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
    return ErrorResponse(
        error=message,
        details={"status_code": status_code}
    ).model_dump()


def build_success_response(message: str, data: Any = None) -> Dict[str, Any]:
    """
    Build a standardized success response.

    Args:
        message: Success message
        data: Optional response data

    Returns:
        Success response dictionary
    """
    return SuccessResponse(
        success=True,
        message=message,
        data=data
    ).model_dump()


def create_bug_report_template(title: str, steps: str, expected: str, actual: str) -> str:
    """
    Create a template for bug reports.

    Args:
        title: Bug title
        steps: Steps to reproduce
        expected: Expected behavior
        actual: Actual behavior

    Returns:
        Bug report markdown template
    """
    return f"""
# {title}

## Bug Description
A bug has been identified that needs to be addressed.

## Steps to Reproduce
{steps}

## Expected Behavior
{expected}

## Actual Behavior
{actual}

## Additional Context
Bug reported on {datetime.now().strftime('%Y-%m-%d')}
"""


def create_feature_request_template(title: str, description: str, user_value: str, acceptance_criteria: str) -> str:
    """
    Create a template for feature requests.

    Args:
        title: Feature title
        description: Description of the feature
        user_value: Value to users
        acceptance_criteria: Acceptance criteria

    Returns:
        Feature request markdown template
    """
    return f"""
# {title}

## Feature Description
{description}

## User Value
{user_value}

## Acceptance Criteria
{acceptance_criteria}

## Additional Notes
Feature requested on {datetime.now().strftime('%Y-%m-%d')}
"""
