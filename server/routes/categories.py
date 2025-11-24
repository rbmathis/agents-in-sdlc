"""
Purpose: Blueprint exposing category-related endpoints.
Provides an endpoint to list all categories with their id and name.
"""
from flask import jsonify, Response, Blueprint
from models import db, Category
from sqlalchemy.orm import Query

# Create a Blueprint for categories routes
categories_bp = Blueprint('categories', __name__)

def get_categories_base_query() -> Query:
    """
    Get the base query for categories.
    
    Returns:
        Query: SQLAlchemy query object for categories
    """
    return db.session.query(Category)

@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    """
    Retrieve all categories with their id and name.
    
    Returns:
        Response: JSON array of category objects containing id and name
    """
    categories_query = get_categories_base_query().all()
    
    # Convert to dictionary format with id and name
    categories_list = [{"id": category.id, "name": category.name} for category in categories_query]
    
    return jsonify(categories_list)
