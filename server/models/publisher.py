from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Publisher(BaseModel):
    """
    Publisher model representing a game publisher seeking crowdfunding.
    
    Attributes:
        id: Primary key
        name: Publisher name (required, unique, min 2 characters)
        description: Publisher description (optional, min 10 characters if provided)
        games: Relationship to Game models (one-to-many)
    """
    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one publisher has many games
    games = relationship("Game", back_populates="publisher")

    @validates('name')
    def validate_name(self, key, name):
        """
        Validate publisher name meets minimum length requirements.
        
        Args:
            key: The attribute name being validated
            name: The publisher name to validate
            
        Returns:
            The validated publisher name
        """
        return self.validate_string_length('Publisher name', name, min_length=2)

    @validates('description')
    def validate_description(self, key, description):
        """
        Validate publisher description meets minimum length requirements.
        
        Args:
            key: The attribute name being validated
            description: The description to validate
            
        Returns:
            The validated description
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)

    def __repr__(self):
        """
        Return string representation of the Publisher instance.
        
        Returns:
            String representation with publisher name
        """
        return f'<Publisher {self.name}>'

    def to_dict(self):
        """
        Convert Publisher instance to dictionary representation for API responses.
        
        Returns:
            Dictionary containing publisher data including game count
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }