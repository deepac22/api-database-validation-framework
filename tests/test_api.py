import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

class TestPolicyAPI:
    
    def test_health_check(self, test_client):
        response = test_client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_unauthorized_access(self, test_client):
        response = test_client.get('/policies')
        assert response.status_code == 401
        data = response.get_json()
        assert 'Unauthorized' in data['error']
    
    def test_create_policy(self, test_client, auth_headers):
        response = test_client.post('/policies', json={
            'title': 'Data Security Policy',
            'description': 'Policy for securing sensitive data',
            'version': '2.0',
            'status': 'active'
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Data Security Policy'
        assert data['status'] == 'active'
    
    def test_create_policy_missing_title(self, test_client, auth_headers):
        response = test_client.post('/policies', json={
            'description': 'Missing title'
        }, headers=auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert 'Title and description are required' in data['error']
    
    def test_create_policy_missing_description(self, test_client, auth_headers):
        response = test_client.post('/policies', json={
            'title': 'Missing Description'
        }, headers=auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert 'Title and description are required' in data['error']
    
    def test_get_policies(self, test_client, auth_headers):
        response = test_client.get('/policies', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_get_policy_by_id(self, test_client, auth_headers):
        create_resp = test_client.post('/policies', json={
            'title': 'Test Policy',
            'description': 'Test description',
            'version': '1.0'
        }, headers=auth_headers)
        policy_id = create_resp.get_json()['id']
        
        response = test_client.get(f'/policies/{policy_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'Test Policy'
    
    def test_get_nonexistent_policy(self, test_client, auth_headers):
        response = test_client.get('/policies/9999', headers=auth_headers)
        assert response.status_code == 404
        data = response.get_json()
        assert 'Policy not found' in data['error']
    
    def test_update_policy(self, test_client, auth_headers):
        create_resp = test_client.post('/policies', json={
            'title': 'Old Title',
            'description': 'Old description',
            'version': '1.0'
        }, headers=auth_headers)
        policy_id = create_resp.get_json()['id']
        
        response = test_client.put(f'/policies/{policy_id}', json={
            'title': 'New Title',
            'version': '2.0'
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'New Title'
        assert data['version'] == '2.0'
    
    def test_update_nonexistent_policy(self, test_client, auth_headers):
        response = test_client.put('/policies/9999', json={
            'title': 'New Title'
        }, headers=auth_headers)
        assert response.status_code == 404
        data = response.get_json()
        assert 'Policy not found' in data['error']
    
    def test_delete_policy(self, test_client, auth_headers):
        create_resp = test_client.post('/policies', json={
            'title': 'To Delete',
            'description': 'This policy will be deleted',
            'version': '1.0',
            'status': 'draft'
        }, headers=auth_headers)
        policy_id = create_resp.get_json()['id']
        
        response = test_client.delete(f'/policies/{policy_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'Policy deleted' in data['message']
        
        get_response = test_client.get(f'/policies/{policy_id}', headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_active_policy_fails(self, test_client, auth_headers):
        create_resp = test_client.post('/policies', json={
            'title': 'Active Policy',
            'description': 'This is active',
            'version': '1.0',
            'status': 'active'
        }, headers=auth_headers)
        policy_id = create_resp.get_json()['id']
        
        response = test_client.delete(f'/policies/{policy_id}', headers=auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot delete an active policy' in data['error']
    
    def test_delete_nonexistent_policy(self, test_client, auth_headers):
        response = test_client.delete('/policies/9999', headers=auth_headers)
        assert response.status_code == 404
        data = response.get_json()
        assert 'Policy not found' in data['error']