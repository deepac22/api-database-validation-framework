from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Use SQLite for simplicity (mimics a real database)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/policies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

@app.route('/policies', methods=['GET'])
def get_policies():
    policies = Policy.query.all()
    return jsonify([p.to_dict() for p in policies])

@app.route('/policies/<int:id>', methods=['GET'])
def get_policy(id):
    policy = Policy.query.get(id)
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    return jsonify(policy.to_dict())

@app.route('/policies', methods=['POST'])
def create_policy():
    data = request.get_json()
    if not data or 'title' not in data or 'description' not in data:
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
def update_policy(id):
    policy = Policy.query.get(id)
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    data = request.get_json()
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
def delete_policy(id):
    policy = Policy.query.get(id)
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    db.session.delete(policy)
    db.session.commit()
    return jsonify({'message': 'Policy deleted'}), 200

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)