from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)

# Use PostgreSQL from environment
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SUPABASE_URI', 'sqlite:///../database/policies.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

API_KEY = os.getenv('API_KEY', 'supersecretkey123')

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='draft')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'version': self.version,
            'status': self.status
        }

def require_api_key(f):
    """Decorator to check API key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/policies', methods=['GET'])
@require_api_key
def get_policies():
    policies = Policy.query.all()
    return jsonify([p.to_dict() for p in policies])

@app.route('/policies/<int:id>', methods=['GET'])
@require_api_key
def get_policy(id):
    policy = Policy.query.get(id)
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    return jsonify(policy.to_dict())

@app.route('/policies', methods=['POST'])
@require_api_key
def create_policy():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'title' not in data or 'description' not in data:
        return jsonify({'error': 'Title and description are required'}), 400
    
    policy = Policy(
        title=data['title'],
        description=data['description'],
        version=data.get('version', '1.0'),
        status=data.get('status', 'draft')
    )
    db.session.add(policy)
    db.session.commit()
    return jsonify(policy.to_dict()), 201

@app.route('/policies/<int:id>', methods=['PUT'])
@require_api_key
def update_policy(id):
    policy = Policy.query.get(id)
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' in data:
        policy.title = data['title']
    if 'description' in data:
        policy.description = data['description']
    if 'version' in data:
        policy.version = data['version']
    if 'status' in data:
        policy.status = data['status']
    
    db.session.commit()
    return jsonify(policy.to_dict())

@app.route('/policies/<int:id>', methods=['DELETE'])
@require_api_key
def delete_policy(id):
    policy = Policy.query.get(id)
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    # Business logic: cannot delete active policies
    if policy.status == 'active':
        return jsonify({'error': 'Cannot delete an active policy'}), 400
    
    db.session.delete(policy)
    db.session.commit()
    return jsonify({'message': 'Policy deleted successfully'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)