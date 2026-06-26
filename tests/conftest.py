import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.app import app, db
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY', 'supersecretkey123')

@pytest.fixture(scope="session")
def test_client():
    """Create a test client with in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
    
    with app.test_client() as client:
        yield client
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def auth_headers():
    """Return headers with API key."""
    return {'X-API-Key': API_KEY}