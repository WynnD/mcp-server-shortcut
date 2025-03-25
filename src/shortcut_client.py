"""
Shortcut API client for interacting with the Shortcut.com API.

This module handles API authentication and requests to the Shortcut API.
"""

import json
import logging
import requests
import httpx
from typing import Dict, List, Optional, Union, Any

from . import config

logger = logging.getLogger(__name__)

class ShortcutClient:
    """Client for interacting with the Shortcut API."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Shortcut client.

        Args:
            api_token: Optional API token. If not provided, it will be loaded from config.
        """
        self.api_token = api_token or config.SHORTCUT_API_TOKEN
        self.base_url = config.SHORTCUT_API_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Shortcut-Token": self.api_token
        }

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Union[Dict, List, None]:
        """
        Make a synchronous request to the Shortcut API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            data: Optional request body data

        Returns:
            Response data as dictionary, list, or None
        
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(
                    url, headers=self.headers, params=params, data=json.dumps(data) if data else None
                )
            elif method.upper() == "PUT":
                response = requests.put(
                    url, headers=self.headers, params=params, data=json.dumps(data) if data else None
                )
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            
            if response.status_code == 204:
                return None
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Shortcut API: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    logger.error(f"API error details: {error_details}")
                except ValueError:
                    logger.error(f"API error response: {e.response.text}")
            
            raise Exception(f"Error making request to Shortcut API: {str(e)}")

    async def _make_request_async(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Union[Dict, List, None]:
        """
        Make an asynchronous request to the Shortcut API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            data: Optional request body data

        Returns:
            Response data as dictionary, list, or None
        
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(
                        url, headers=self.headers, params=params, json=data
                    )
                elif method.upper() == "PUT":
                    response = await client.put(
                        url, headers=self.headers, params=params, json=data
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                
                if response.status_code == 204:
                    return None
                
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Error making request to Shortcut API: {str(e)}")
                try:
                    error_details = e.response.json()
                    logger.error(f"API error details: {error_details}")
                    return {"error": str(e), "details": error_details}
                except ValueError:
                    logger.error(f"API error response: {e.response.text}")
                    return {"error": str(e), "details": {"raw_response": e.response.text}}
            
            except Exception as e:
                logger.error(f"Unexpected error in API request: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}

    # Synchronous methods
    def get_stories(self, params: Optional[Dict] = None) -> List[Dict]:
        """
        Get stories (tickets) from Shortcut.
        
        Args:
            params: Optional query parameters
            
        Returns:
            List of stories
        """
        return self._make_request("GET", "stories", params=params) or []

    def search_stories(self, query: str, page_size: int = 25) -> List[Dict]:
        """
        Search for stories using Shortcut's search functionality.
        
        Args:
            query: Search query string
            page_size: Maximum number of results to return
            
        Returns:
            List of matching stories
        """
        params = {"query": query, "page_size": page_size}
        results = self._make_request("GET", "search/stories", params=params)
        return results.get("data", []) if results else []

    def get_story_by_id(self, story_id: int) -> Optional[Dict]:
        """
        Get a specific story by ID.
        
        Args:
            story_id: Story/ticket ID
            
        Returns:
            Story details or None if not found
        """
        try:
            return self._make_request("GET", f"stories/{story_id}")
        except Exception:
            return None

    def get_members(self) -> List[Dict]:
        """
        Get all workspace members.
        
        Returns:
            List of members
        """
        return self._make_request("GET", "members") or []

    def create_story(self, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a new story in Shortcut.
        
        Args:
            data: Story data
            
        Returns:
            Created story or None if creation failed
        """
        try:
            return self._make_request("POST", "stories", data=data)
        except Exception as e:
            logger.error(f"Error creating story: {str(e)}")
            return None

    def update_story(self, story_id: int, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update an existing story in Shortcut.
        
        Args:
            story_id: Story ID to update
            data: Updated story data
            
        Returns:
            Updated story or None if update failed
        """
        try:
            return self._make_request("PUT", f"stories/{story_id}", data=data)
        except Exception as e:
            logger.error(f"Error updating story: {str(e)}")
            return None

    def add_comment(self, story_id: int, text: str) -> Optional[Dict]:
        """
        Add a comment to a story.
        
        Args:
            story_id: Story ID to comment on
            text: Comment text
            
        Returns:
            Created comment or None if creation failed
        """
        try:
            data = {"text": text}
            return self._make_request("POST", f"stories/{story_id}/comments", data=data)
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            return None

    def get_workflow_states(self) -> List[Dict]:
        """
        Get all workflow states.
        
        Returns:
            List of workflow states grouped by workflow
        """
        workflows = self._make_request("GET", "workflows") or []
        return workflows

    def get_projects(self) -> List[Dict]:
        """
        Get all projects.
        
        Returns:
            List of projects
        """
        return self._make_request("GET", "projects") or []

    # Async methods
    async def get_stories_async(self, params: Optional[Dict] = None) -> List[Dict]:
        """
        Get stories (tickets) from Shortcut asynchronously.
        
        Args:
            params: Optional query parameters
            
        Returns:
            List of stories
        """
        result = await self._make_request_async("GET", "stories", params=params)
        if isinstance(result, dict) and "error" in result:
            return []
        return result or []

    async def search_stories_async(self, query: str, page_size: int = 25) -> List[Dict]:
        """
        Search for stories using Shortcut's search functionality asynchronously.
        
        Args:
            query: Search query string
            page_size: Maximum number of results to return
            
        Returns:
            List of matching stories
        """
        params = {"query": query, "page_size": page_size}
        results = await self._make_request_async("GET", "search/stories", params=params)
        if isinstance(results, dict) and "error" in results:
            return []
        return results.get("data", []) if results else []

    async def get_story_by_id_async(self, story_id: int) -> Optional[Dict]:
        """
        Get a specific story by ID asynchronously.
        
        Args:
            story_id: Story/ticket ID
            
        Returns:
            Story details or None if not found
        """
        result = await self._make_request_async("GET", f"stories/{story_id}")
        if isinstance(result, dict) and "error" in result:
            return None
        return result

    async def create_story_async(self, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a new story in Shortcut asynchronously.
        
        Args:
            data: Story data
            
        Returns:
            Created story or None if creation failed
        """
        result = await self._make_request_async("POST", "stories", data=data)
        if isinstance(result, dict) and "error" in result:
            return None
        return result

    async def update_story_async(self, story_id: int, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update an existing story in Shortcut asynchronously.
        
        Args:
            story_id: Story ID to update
            data: Updated story data
            
        Returns:
            Updated story or None if update failed
        """
        result = await self._make_request_async("PUT", f"stories/{story_id}", data=data)
        if isinstance(result, dict) and "error" in result:
            return None
        return result

    async def add_comment_async(self, story_id: int, text: str) -> Optional[Dict]:
        """
        Add a comment to a story asynchronously.
        
        Args:
            story_id: Story ID to comment on
            text: Comment text
            
        Returns:
            Created comment or None if creation failed
        """
        data = {"text": text}
        result = await self._make_request_async("POST", f"stories/{story_id}/comments", data=data)
        if isinstance(result, dict) and "error" in result:
            return None
        return result

    async def get_workflow_states_async(self) -> List[Dict]:
        """
        Get all workflow states asynchronously.
        
        Returns:
            List of workflow states grouped by workflow
        """
        result = await self._make_request_async("GET", "workflows")
        if isinstance(result, dict) and "error" in result:
            return []
        return result or []

    async def get_projects_async(self) -> List[Dict]:
        """
        Get all projects asynchronously.
        
        Returns:
            List of projects
        """
        result = await self._make_request_async("GET", "projects")
        if isinstance(result, dict) and "error" in result:
            return []
        return result or []
