from flask import Flask, jsonify, request
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from flask_redis import FlaskRedis
import json

app = Flask(__name__)
app.debug = True
app.config['MONGODB_SETTINGS'] = {
    'db': 'mydatabase',
    'host': 'mongodb://mongodb:27017/mydatabase'
}
app.config['REDIS_URL'] = 'redis://redis:6379/0'

CORS(app)

db = MongoEngine(app)
redis_store = FlaskRedis(app)

class User(db.Document):
    name = db.StringField(required=True)
    age = db.IntField(required=True)

@app.route('/api/users', methods=['GET'])
def get_users():
    # Check Redis cache first
    users_data = redis_store.get('users')
    # app.logger.info(      users_data)
    if users_data:
        users = users_data.decode('utf-8')  # Convert binary to string
    else:
        users = User.objects().to_json()
        # app.logger.info(users)
        # Store data in Redis cache
        redis_store.set('users', users)
    return users, 200

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.objects.get_or_404(id=user_id)
    return jsonify(user), 200

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(name=data['name'], age=data['age'])
    user.save()
    # Clear Redis cache
    redis_store.delete('users')
    return jsonify(user), 201


@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.objects.get_or_404(id=user_id)
    user.name = data['name']
    user.age = data['age']
    user.save()
    # Clear Redis cache
    redis_store.delete('users')
    return jsonify(user), 200

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.objects.get_or_404(id=user_id)
    user.delete()
    # Clear Redis cache
    redis_store.delete('users')
    return jsonify({'message': 'User deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)