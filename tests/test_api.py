import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json

class TestPolicyAPI:
    
    def test_create_policy(self, test_client):
        response = test_client.post('/policies', json={
            'title': 'Data Security Policy',
            'description': 'Policy for securing sensitive data',
            'version': '2.0',
            'status': 'active'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Data Security Policy'
        assert data['status'] == 'active'
    
    def test_get_policies(self, test_client):
        response = test_client.get('/policies')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_get_policy_by_id(self, test_client):
        # Create a policy first
        create_resp = test_client.post('/policies', json={
            'title': 'Test Policy',
            'description': 'Test description',
            'version': '1.0'
        })
        policy_id = create_resp.get_json()['id']
        
        # Get it by ID
        response = test_client.get(f'/policies/{policy_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Test Policy'
    
    def test_update_policy(self, test_client):
        # Create a policy
        create_resp = test_client.post('/policies', json={
            'title': 'Old Title',
            'description': 'Old description',
            'version': '1.0'
        })
        policy_id = create_resp.get_json()['id']
        
        # Update it
        response = test_client.put(f'/policies/{policy_id}', json={
            'title': 'New Title',
            'version': '2.0'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'New Title'
        assert data['version'] == '2.0'
    
    def test_delete_policy(self, test_client):
        # Create a policy
        create_resp = test_client.post('/policies', json={
            'title': 'To Delete',
            'description': 'This policy will be deleted',
            'version': '1.0'
        })
        policy_id = create_resp.get_json()['id']
        
        # Delete it
        response = test_client.delete(f'/policies/{policy_id}')
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = test_client.get(f'/policies/{policy_id}')
        assert get_response.status_code == 404
    
    def test_create_policy_missing_fields(self, test_client):
        response = test_client.post('/policies', json={
            'title': 'Missing Description'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data