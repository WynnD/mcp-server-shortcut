"""
MCP Server for Shortcut.com integration.

This server provides an interface for accessing and searching Shortcut tickets.
"""

import json
from typing import Dict, List, Any, Optional, Union, Tuple

from flask import Flask, request, jsonify

import config
from shortcut_client import ShortcutClient
import utils

app = Flask(__name__)
shortcut_client = ShortcutClient()


@app.route('/health', methods=['GET'])
def health_check() -> Tuple[Dict[str, Any], int]:
    """
    Health check endpoint.

    Returns:
        Tuple of response and status code
    """
    return jsonify({"status": "ok"}), 200


@app.route('/tickets', methods=['GET'])
def get_tickets() -> Tuple[Dict[str, Any], int]:
    """
    Get tickets from Shortcut.

    Query parameters:
    - limit: Maximum number of tickets to return
    - state: Filter by workflow state name

    Returns:
        Tuple of response and status code
    """
    try:
        # Extract query parameters
        limit = request.args.get('limit', default=10, type=int)
        state = request.args.get('state', default=None, type=str)

        # Build params for API request
        params = {}
        if state:
            # In a full implementation, you might want to translate between
            # state names and IDs using the workflows endpoint
            params['workflow_state_name'] = state

        # Get stories from Shortcut
        stories = shortcut_client.get_stories(params)

        # Limit results
        stories = stories[:limit] if limit > 0 else stories

        # Format for display
        formatted_stories = utils.format_search_results(stories)

        return jsonify({
            "tickets": formatted_stories,
            "count": len(formatted_stories)
        }), 200

    except Exception as e:
        return jsonify(utils.build_error_response(str(e))), 500


@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Get a specific ticket by ID.

    Args:
        ticket_id: Ticket ID to retrieve

    Returns:
        Tuple of response and status code
    """
    try:
        story = shortcut_client.get_story_by_id(ticket_id)

        if not story:
            return jsonify(utils.build_error_response(
                f"Ticket with ID {ticket_id} not found", 404
            )), 404

        formatted_story = utils.format_story_for_display(story)

        return jsonify({
            "ticket": formatted_story
        }), 200

    except Exception as e:
        return jsonify(utils.build_error_response(str(e))), 500


@app.route('/search', methods=['GET', 'POST'])
def search_tickets() -> Tuple[Dict[str, Any], int]:
    """
    Search for tickets in Shortcut.

    Query or body parameters:
    - query: Search query string
    - limit: Maximum number of results to return

    Returns:
        Tuple of response and status code
    """
    try:
        # Get query parameter from either query string or JSON body
        if request.method == 'GET':
            query = request.args.get('query', '')
            limit = request.args.get('limit', default=10, type=int)
        else:  # POST
            data = request.get_json(silent=True) or {}
            query = data.get('query', '')
            limit = data.get('limit', 10)

        if not query:
            return jsonify(utils.build_error_response(
                "Search query is required", 400
            )), 400

        # Search for stories
        stories = shortcut_client.search_stories(query)

        # Limit results
        stories = stories[:limit] if limit > 0 else stories

        # Format for display
        formatted_stories = utils.format_search_results(stories)

        return jsonify({
            "results": formatted_stories,
            "count": len(formatted_stories),
            "query": query
        }), 200

    except Exception as e:
        return jsonify(utils.build_error_response(str(e))), 500


if __name__ == '__main__':
    app.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=config.DEBUG_MODE
    )
