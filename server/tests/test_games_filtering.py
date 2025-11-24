"""
Purpose: Unit tests for games filtering functionality.
Tests filtering games by category and publisher.
"""
import unittest
import json
from typing import Dict, List, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.games import games_bp

class TestGamesFiltering(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"},
            {"name": "Agile Studios"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"},
            {"name": "Puzzle"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 1,
                "category_index": 1,
                "star_rating": 4.2
            },
            {
                "title": "Code Review Quest",
                "description": "Master the art of code reviews",
                "publisher_index": 0,
                "category_index": 2,
                "star_rating": 4.7
            }
        ]
    }
    
    # API paths
    GAMES_API_PATH: str = '/api/games'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the games blueprint
        self.app.register_blueprint(games_bp)
        
        # Initialize the test client
        self.client = self.app.test_client()
        
        # Initialize in-memory database for testing
        db.init_app(self.app)
        
        # Create tables and seed data
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        # Create test publishers
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create test games
        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")
            
            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))
            
        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_filter_games_by_category(self) -> None:
        """Test filtering games by category ID"""
        # Get category ID for "Strategy"
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        strategy_game = [g for g in games if g['category']['name'] == 'Strategy'][0]
        category_id = strategy_game['category']['id']
        
        # Act - filter by category
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id={category_id}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['category']['name'], 'Strategy')
        self.assertEqual(data[0]['title'], 'Pipeline Panic')

    def test_filter_games_by_publisher(self) -> None:
        """Test filtering games by publisher ID"""
        # Get publisher ID for "DevGames Inc" (has 2 games)
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        devgames_game = [g for g in games if g['publisher']['name'] == 'DevGames Inc'][0]
        publisher_id = devgames_game['publisher']['id']
        
        # Act - filter by publisher
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher_id={publisher_id}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        for game in data:
            self.assertEqual(game['publisher']['name'], 'DevGames Inc')

    def test_filter_games_by_category_and_publisher(self) -> None:
        """Test filtering games by both category and publisher"""
        # Get IDs for Strategy category and DevGames Inc publisher
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        target_game = [g for g in games if g['title'] == 'Pipeline Panic'][0]
        category_id = target_game['category']['id']
        publisher_id = target_game['publisher']['id']
        
        # Act - filter by both
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id={category_id}&publisher_id={publisher_id}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Pipeline Panic')
        self.assertEqual(data[0]['category']['name'], 'Strategy')
        self.assertEqual(data[0]['publisher']['name'], 'DevGames Inc')

    def test_filter_games_no_results(self) -> None:
        """Test filtering games with no matching results"""
        # Act - use non-existent category ID
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id=999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)

    def test_filter_games_invalid_category_id(self) -> None:
        """Test filtering with invalid category_id parameter"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id=invalid')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid category_id parameter')

    def test_filter_games_invalid_publisher_id(self) -> None:
        """Test filtering with invalid publisher_id parameter"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}?publisher_id=invalid')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid publisher_id parameter')

    def test_filter_games_with_one_filter_empty_string(self) -> None:
        """Test that empty string filter parameters are ignored"""
        # Act - pass empty string for category_id
        response = self.client.get(f'{self.GAMES_API_PATH}?category_id=')
        data = self._get_response_data(response)
        
        # Assert - should return all games
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))

if __name__ == '__main__':
    unittest.main()
