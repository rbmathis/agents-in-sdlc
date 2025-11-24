"""Unit tests for the games API routes covering list and detail endpoints."""

import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Game, Publisher, Category, db
from routes.games import games_bp

class TestGamesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"}
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

    def _create_additional_games(self, count: int) -> None:
        """Helper method to create additional games for pagination tests"""
        with self.app.app_context():
            publisher: Publisher = Publisher.query.first()
            category: Category = Category.query.first()

            for index in range(count):
                db.session.add(Game(
                    title=f"Extra Game {index}",
                    description="Test description for pagination",
                    star_rating=3.0 + (index % 2),
                    publisher=publisher,
                    category=category
                ))
            db.session.commit()

    def test_get_games_success(self) -> None:
        """Test successful retrieval of multiple games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        payload = self._get_response_data(response)
        games = payload["games"]
        pagination = payload["pagination"]
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(games), len(self.TEST_DATA["games"]))
        self.assertEqual(pagination["total_items"], len(self.TEST_DATA["games"]))
        self.assertEqual(pagination["page"], 1)
        self.assertEqual(pagination["per_page"], 20)
        
        # Verify all games using loop instead of manual testing
        games_by_title = {game['title']: game for game in games}

        for test_game in self.TEST_DATA["games"]:
            fetched_game = games_by_title[test_game["title"]]
            test_publisher = self.TEST_DATA["publishers"][test_game["publisher_index"]]
            test_category = self.TEST_DATA["categories"][test_game["category_index"]]

            self.assertEqual(fetched_game['publisher']['name'], test_publisher["name"])
            self.assertEqual(fetched_game['category']['name'], test_category["name"])
            self.assertEqual(fetched_game['starRating'], test_game["star_rating"])

    def test_get_games_structure(self) -> None:
        """Test the response structure for games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        payload = self._get_response_data(response)
        games = payload["games"]
        pagination = payload["pagination"]
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(payload, dict)
        self.assertIn('games', payload)
        self.assertIn('pagination', payload)
        self.assertIsInstance(games, list)
        self.assertEqual(len(games), len(self.TEST_DATA["games"]))
        self.assertIsInstance(pagination, dict)
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'starRating']
        for field in required_fields:
            self.assertIn(field, games[0])

    def test_get_game_by_id_success(self) -> None:
        """Test successful retrieval of a single game by ID"""
        # Get the first game's ID from the list endpoint
        response = self.client.get(self.GAMES_API_PATH)
        games_payload = self._get_response_data(response)
        target_title = self.TEST_DATA["games"][0]["title"]
        matching_game = next(game for game in games_payload['games'] if game['title'] == target_title)
        game_id = matching_game['id']
        
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        # Assert
        first_game = self.TEST_DATA["games"][0]
        first_publisher = self.TEST_DATA["publishers"][first_game["publisher_index"]]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], first_game["title"])
        self.assertEqual(data['publisher']['name'], first_publisher["name"])
        
    def test_get_game_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent game by ID"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    def test_pagination_metadata_with_custom_page(self) -> None:
        """Test that pagination metadata updates correctly when requesting specific pages"""
        # Arrange
        self._create_additional_games(3)

        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}?page=2&per_page=2')
        payload = self._get_response_data(response)
        pagination = payload['pagination']

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(pagination['page'], 2)
        self.assertEqual(pagination['per_page'], 2)
        self.assertGreaterEqual(pagination['total_items'], 5)
        self.assertTrue(pagination['total_pages'] >= 3)
        self.assertTrue(pagination['has_previous'])

    def test_invalid_pagination_parameter_returns_error(self) -> None:
        """Test API returns an error when pagination params are invalid"""
        response = self.client.get(f'{self.GAMES_API_PATH}?page=abc')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Pagination parameters must be integers")

    def test_sorting_by_star_rating_descending(self) -> None:
        """Test sorting games by star rating in descending order"""
        response = self.client.get(f'{self.GAMES_API_PATH}?sort=star_rating&order=desc')
        payload = self._get_response_data(response)
        games = payload['games']

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(games), 2)
        self.assertGreaterEqual(games[0]['starRating'], games[1]['starRating'])

    def test_invalid_sort_parameter_returns_error(self) -> None:
        """Test API returns an error when sort parameter is unsupported"""
        response = self.client.get(f'{self.GAMES_API_PATH}?sort=unknown_field')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Invalid sort parameter")

if __name__ == '__main__':
    unittest.main()