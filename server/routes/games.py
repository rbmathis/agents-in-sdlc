from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from typing import Optional

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    """
    Build base query for games with joined publisher and category relationships.
    
    Returns:
        SQLAlchemy Query object with games joined to publishers and categories
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
    Get all games with their publisher and category information.
    
    Returns:
        JSON response containing list of all games
    """
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    # Apply publisher filter if provided
    publisher_id: Optional[str] = request.args.get('publisher_id')
    if publisher_id:
        try:
            games_query = games_query.filter(Game.publisher_id == int(publisher_id))
        except ValueError:
            return jsonify({"error": "Invalid publisher_id parameter"}), 400
    
    # Execute query and convert results
    games_list = [game.to_dict() for game in games_query.all()]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    """
    Get a specific game by ID with publisher and category information.
    
    Args:
        id: The game ID to retrieve
        
    Returns:
        JSON response containing game data, or 404 error if not found
    """
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int]:
    """Create a new game"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['title', 'description', 'category_id', 'publisher_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Verify that publisher exists
        publisher = db.session.query(Publisher).filter(Publisher.id == data['publisher_id']).first()
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 404
        
        # Verify that category exists
        category = db.session.query(Category).filter(Category.id == data['category_id']).first()
        if not category:
            return jsonify({"error": "Category not found"}), 404
        
        # Create new game
        new_game = Game(
            title=data['title'],
            description=data['description'],
            category_id=data['category_id'],
            publisher_id=data['publisher_id'],
            star_rating=data.get('star_rating')
        )
        
        # Add to database
        db.session.add(new_game)
        db.session.commit()
        
        # Fetch the game with relationships for proper response
        created_game = get_games_base_query().filter(Game.id == new_game.id).first()
        
        return jsonify(created_game.to_dict()), 201
        
    except ValueError as e:
        # Handle validation errors from model validators
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int]:
    """Update an existing game"""
    try:
        # Find the game
        game = db.session.query(Game).filter(Game.id == id).first()
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update fields if provided
        if 'title' in data:
            game.title = data['title']
        if 'description' in data:
            game.description = data['description']
        if 'star_rating' in data:
            game.star_rating = data['star_rating']
        
        # Update publisher_id if provided and verify it exists
        if 'publisher_id' in data:
            publisher = db.session.query(Publisher).filter(Publisher.id == data['publisher_id']).first()
            if not publisher:
                return jsonify({"error": "Publisher not found"}), 404
            game.publisher_id = data['publisher_id']
        
        # Update category_id if provided and verify it exists
        if 'category_id' in data:
            category = db.session.query(Category).filter(Category.id == data['category_id']).first()
            if not category:
                return jsonify({"error": "Category not found"}), 404
            game.category_id = data['category_id']
        
        # Commit changes
        db.session.commit()
        
        # Fetch the updated game with relationships for proper response
        updated_game = get_games_base_query().filter(Game.id == id).first()
        
        return jsonify(updated_game.to_dict()), 200
        
    except ValueError as e:
        # Handle validation errors from model validators
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    """Delete a game"""
    try:
        # Find the game
        game = db.session.query(Game).filter(Game.id == id).first()
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Delete the game
        db.session.delete(game)
        db.session.commit()
        
        return Response('', 204)
        
    except Exception as e:
        # Handle unexpected errors
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

