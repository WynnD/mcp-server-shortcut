"""
Shortcut API client for interacting with the Shortcut.com API.

This module handles API authentication and requests to the Shortcut API.
"""

import json
import requests
from typing import Dict, List, Optional, Union, Any

import config


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
        Make a request to the Shortcut API.

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
            # Log error details here if needed
            raise Exception(f"Error making request to Shortcut API: {str(e)}")

    def get_stories(self, params: Optional[Dict] = None) -> List[Dict]:
        """
        Get stories (tickets) from Shortcut.
        
        Args:
            params: Optional query parameters
            
        Returns:
            List of stories
        """
        return self._make_request("GET", "stories", params=params) or []

    def search_stories(self, query: str) -> List[Dict]:
        """
        Search for stories using Shortcut's search functionality.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching stories
        """
        data = {"query": query}
        results = self._make_request("POST", "search/stories", data=data)
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
