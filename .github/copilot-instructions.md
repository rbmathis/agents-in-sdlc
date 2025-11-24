# Tailspin Toys Crowd Funding Development Guidelines

This is a crowdfunding platform for games with a developer theme. The application uses a Flask backend API with SQLAlchemy ORM for database interactions, and an Astro/Svelte frontend with Tailwind CSS for styling. Please follow these guidelines when contributing:

## Agent notes

- Do not generate summary markdown files upon completion of a task
- Always use absolute paths when running scripts and BASH commands

## Code standards

### Required Before Each Commit

- Run Python tests to ensure backend functionality
- For frontend changes, run builds in the client directory to verify build success and the end-to-end tests, to ensure everything works correctly
- When making API changes, update and run the corresponding tests to ensure everything works correctly
- When updating models, ensure database migrations are included if needed
- When adding new functionality, make sure you update the README
- Make sure all guidance in the Copilot Instructions file is updated with any relevant changes, including to project structure and scripts, and programming guidance

### Code formatting requirements

- When writing Python, you must use type hints for return values and function parameters.
- Every function should have docstrings or the language equivalent
- Before imports or any code, add a comment block that explains the purpose of the file.

### Python Formatting Standards

All Python code must follow PEP 8 style guidelines with the following specific requirements:

#### General Formatting
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters for code, 72 for docstrings
- Use blank lines to separate logical sections:
  - Two blank lines before top-level class and function definitions
  - One blank line between methods in a class
- UTF-8 encoding for all Python files
- Unix-style line endings (LF, not CRLF)

#### Import Organization
Imports must be organized in the following order, with each group separated by a blank line:
1. Standard library imports
2. Related third-party imports (e.g., Flask, SQLAlchemy)
3. Local application imports

Example:
```python
import os
import json
from typing import Dict, List, Optional

from flask import Flask, jsonify, Response
from sqlalchemy.orm import Query

from models import db, Category
from utils.database import get_connection_string
```

#### Naming Conventions
- Classes: `PascalCase` (e.g., `GameModel`, `CategoryService`)
- Functions and methods: `snake_case` (e.g., `get_categories`, `validate_input`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RATING`, `API_VERSION`)
- Private methods/attributes: prefix with single underscore `_private_method`
- Variables: `snake_case` (e.g., `user_id`, `game_title`)

### Python Docstring Standards

All Python functions, methods, classes, and modules must include docstrings following Google-style format.

#### Module-Level Docstrings
Every Python file must start with a docstring explaining its purpose:

```python
"""
Purpose: Blueprint exposing category-related endpoints.
Provides an endpoint to list all categories with their id and name.
"""
```

#### Function and Method Docstrings
All functions and methods must include:
- Brief description of what the function does
- Args section listing all parameters with types and descriptions
- Returns section describing return value and type
- Raises section if the function raises exceptions

Example:
```python
def get_categories_base_query() -> Query:
    """
    Get the base query for categories.
    
    Returns:
        Query: SQLAlchemy query object for categories
    """
    return db.session.query(Category)

def validate_string_length(field_name: str, value: Optional[str], min_length: int = 2, 
                          allow_none: bool = False) -> Optional[str]:
    """
    Validate that a string field meets minimum length requirements.
    
    Args:
        field_name: The name of the field being validated (for error messages)
        value: The value to validate (can be None if allow_none is True)
        min_length: Minimum required length (default: 2)
        allow_none: Whether None values are allowed (default: False)
        
    Returns:
        The validated value unchanged if it passes validation, or None if 
        value is None and allow_none is True
        
    Raises:
        ValueError: If validation fails (empty value, wrong type, or too short)
    """
    if value is None:
        if allow_none:
            return value
        else:
            raise ValueError(f"{field_name} cannot be empty")
    
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
        
    if len(value.strip()) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters")
        
    return value
```

#### Class Docstrings
Classes must include a docstring with:
- Brief description of the class purpose
- Attributes section listing all public attributes

Example:
```python
class Game(BaseModel):
    """
    Game model representing a crowdfunding game project.
    
    Attributes:
        id: Primary key
        title: Game title (required, min 2 characters)
        description: Game description (required, min 10 characters)
        star_rating: User rating (0-5 stars, optional)
        category_id: Foreign key to Category
        publisher_id: Foreign key to Publisher
        category: Relationship to Category model
        publisher: Relationship to Publisher model
    """
```

### Python Type Hints Requirements

Type hints are mandatory for all function signatures:

#### Required Type Hints
- All function parameters must have type hints
- All function return values must have type hints (use `None` for no return)
- Use standard library `typing` module for complex types

Examples:
```python
from typing import Dict, List, Optional, Any

def get_game_by_id(game_id: int) -> Optional[Game]:
    """Retrieve a game by its ID."""
    return db.session.query(Game).filter_by(id=game_id).first()

def create_game(title: str, description: str, category_id: int) -> Game:
    """Create a new game instance."""
    game = Game(title=title, description=description, category_id=category_id)
    return game

def process_games(games: List[Game]) -> Dict[str, Any]:
    """Process a list of games and return summary data."""
    return {"count": len(games), "titles": [g.title for g in games]}

def setup_database() -> None:
    """Initialize database tables."""
    db.create_all()
```

#### Type Hint Best Practices
- Use `Optional[Type]` for parameters that can be None
- Use `List[Type]`, `Dict[K, V]` for collections
- Use `Any` sparingly, prefer specific types when possible
- For Flask responses, use `Response` type from `flask` module
- For SQLAlchemy queries, use `Query` type from `sqlalchemy.orm`

### Python and Flask Patterns

- Use SQLAlchemy models for database interactions
- Use Flask blueprints for organizing routes
- Follow RESTful API design principles

### Svelte and Astro Patterns

- Use Svelte for interactive components
- Follow Svelte's reactive programming model
- Create reusable components when functionality is used in multiple places
- Use Astro for page routing and static content

### Styling

- Use Tailwind CSS classes for styling
- Maintain dark mode theme throughout the application
- Use rounded corners for UI elements
- Follow modern UI/UX principles with clean, accessible interfaces

### GitHub Actions workflows

- Follow good security practices
- Make sure to explicitly set the workflow permissions
- Add comments to document what tasks are being performed

## Scripts

- Several scripts exist in the `scripts` folder
- Always use available scripts to perform tasks rather than performing operations manually
- Existing scripts:
    - `scripts/setup-env.sh`: Performs installation of all Python and Node dependencies
    - `scripts/run-server-tests.sh`: Calls setup-env, then runs all Python tests
    - `scripts/start-app.sh`: Calls setup-env, then starts both backend and frontend servers

## Repository Structure

- `server/`: Flask backend code
  - `models/`: SQLAlchemy ORM models
  - `routes/`: API endpoints organized by resource
  - `tests/`: Unit tests for the API
  - `utils/`: Utility functions and helpers
- `client/`: Astro/Svelte frontend code
  - `src/components/`: Reusable Svelte components
  - `src/layouts/`: Astro layout templates
  - `src/pages/`: Astro page routes
  - `src/styles/`: CSS and Tailwind configuration
- `scripts/`: Development and deployment scripts
- `data/`: Database files
- `docs/`: Project documentation
- `README.md`: Project documentation
