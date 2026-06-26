import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.app import app, db
from app.app import Policy

class TestDatabaseValidation:
    
    def test_database_has_policies_table(self, test_client):
        """Check that the policy table exists."""
        with app.app_context():
            # Check if the table exists by querying it
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            assert 'policy' in tables, "Policy table does not exist"
    
    def test_database_has_correct_columns(self, test_client):
        """Check that the policy table has the correct columns."""
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('policy')]
            expected_columns = ['id', 'title', 'description', 'version', 'status']
            for col in expected_columns:
                assert col in columns, f"Column '{col}' missing from policy table"
    
    def test_data_persists_after_api_call(self, test_client):
        """Test that data is properly saved to the database."""
        # Create a policy via API
        response = test_client.post('/policies', json={
            'title': 'Persistence Test',
            'description': 'Testing database persistence',
            'version': '1.0',
            'status': 'draft'
        })
        assert response.status_code == 201
        policy_id = response.get_json()['id']
        
        # Query the database directly
        with app.app_context():
            policy = db.session.get(Policy, policy_id)
            assert policy is not None
            assert policy.title == 'Persistence Test'
            assert policy.description == 'Testing database persistence'
            assert policy.version == '1.0'
            assert policy.status == 'draft'
    
    def test_data_updated_in_database(self, test_client):
        """Test that data is properly updated in the database."""
        # Create a policy
        create_resp = test_client.post('/policies', json={
            'title': 'Update Test',
            'description': 'Original description',
            'version': '1.0'
        })
        policy_id = create_resp.get_json()['id']
        
        # Update it via API
        test_client.put(f'/policies/{policy_id}', json={
            'title': 'Updated Title',
            'version': '2.0'
        })
        
        # Verify in database
        with app.app_context():
            policy = db.session.get(Policy, policy_id)
            assert policy.title == 'Updated Title'
            assert policy.version == '2.0'
    
    def test_data_deleted_from_database(self, test_client):
        """Test that data is properly deleted from the database."""
        # Create a policy
        create_resp = test_client.post('/policies', json={
            'title': 'Delete Test',
            'description': 'To be deleted',
            'version': '1.0'
        })
        policy_id = create_resp.get_json()['id']
        
        # Delete it via API
        test_client.delete(f'/policies/{policy_id}')
        
        # Verify in database
        with app.app_context():
            policy = db.session.get(Policy, policy_id)
            assert policy is None, "Policy should be deleted from database"