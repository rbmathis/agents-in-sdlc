"""Flask routes for the games resource, including listing and detail APIs."""

from flask import jsonify, Response, Blueprint, request
from math import ceil
from models import db, Game, Publisher, Category
from sqlalchemy import asc, desc
from sqlalchemy.orm import Query
from typing import Optional

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 50

def get_games_base_query() -> Query:
    """
    Get the base query for games with joined publisher and category.
    
    Returns:
        Query: SQLAlchemy query object for games
    """
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    """
    Retrieve all games with optional filtering by category and/or publisher.
    
    Query Parameters:
        category_id (int, optional): Filter games by category ID
        publisher_id (int, optional): Filter games by publisher ID
    
    Returns:
        Response: JSON array of game objects
    """
    # Start with the base query
    games_query = get_games_base_query()
    
    # Apply category filter if provided
    category_id: Optional[str] = request.args.get('category_id')
    if category_id:
        try:
            games_query = games_query.filter(Game.category_id == int(category_id))
        except ValueError:
            return jsonify({"error": "Invalid category_id parameter"}), 400
    
    # Apply publisher filter if provided
    publisher_id: Optional[str] = request.args.get('publisher_id')
    if publisher_id:
        try:
            games_query = games_query.filter(Game.publisher_id == int(publisher_id))
        except ValueError:
            return jsonify({"error": "Invalid publisher_id parameter"}), 400
    
    # Apply pagination parameters
    page_param: str = request.args.get('page', '1')
    per_page_param: str = request.args.get('per_page', str(DEFAULT_PAGE_SIZE))

    try:
        page: int = max(int(page_param), 1)
        per_page: int = int(per_page_param)
    except ValueError:
        return jsonify({"error": "Pagination parameters must be integers"}), 400

    if per_page < 1:
        return jsonify({"error": "per_page must be greater than 0"}), 400

    per_page = min(per_page, MAX_PAGE_SIZE)

    # Apply sorting parameters
    sort_field: str = request.args.get('sort', 'title')
    sort_order: str = request.args.get('order', 'asc').lower()
    if sort_order not in ('asc', 'desc'):
        return jsonify({"error": "Invalid order parameter. Must be 'asc' or 'desc'"}), 400

    sort_mapping = {
        'title': Game.title,
        'star_rating': Game.star_rating,
        'id': Game.id,
    }

    if sort_field not in sort_mapping:
        return jsonify({"error": "Invalid sort parameter"}), 400

    sort_column = sort_mapping[sort_field]
    order_callable = asc if sort_order != 'desc' else desc
    games_query = games_query.order_by(order_callable(sort_column))

    # Calculate totals before pagination slicing
    total_items: int = games_query.count()
    total_pages: int = ceil(total_items / per_page) if total_items else 1

    # Apply offset/limit for pagination
    offset_value: int = (page - 1) * per_page
    games_query = games_query.offset(offset_value).limit(per_page)

    # Execute query and convert results
    games_list = [game.to_dict() for game in games_query.all()]

    pagination_metadata = {
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
    
    return jsonify({
        "games": games_list,
        "pagination": pagination_metadata,
    })

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    """
    Retrieve a single game by ID.
    
    Args:
        id (int): The game ID
    
    Returns:
        Response: JSON object of game details or error message
    """
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)
