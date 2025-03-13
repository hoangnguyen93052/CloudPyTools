import time
import random
import threading
import logging
import json
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
from collections import defaultdict

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = 'sqlite:///performance_tuning.db'  # Use your database URL here
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

# ORM Models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(20), default='incomplete')

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Flask app setup
app = Flask(__name__)

# In-memory cache for quick lookups
cache = {}
cache_lock = threading.Lock()

def cache_result(key, value):
    with cache_lock:
        cache[key] = value

def get_cached_result(key):
    with cache_lock:
        return cache.get(key)

def performance_tuning_query(num_users=1000):
    logger.info(f"Generating {num_users} users for performance tuning.")
    session = Session()
    
    # Bulk insert operation
    users = [User(username=f'user{i}', email=f'user{i}@example.com') for i in range(num_users)]
    try:
        session.bulk_save_objects(users)
        session.commit()
        logger.info(f"{num_users} users inserted successfully.")
    except IntegrityError:
        session.rollback()
        logger.error("Integrity error occurred during bulk save.")
    finally:
        session.close()

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    session = Session()
    user = User(username=username, email=email)
    session.add(user)

    try:
        session.commit()
        logger.info(f"User '{username}' created successfully.")
        return jsonify({"message": "User created", "user": {"username": username, "email": email}}), 201
    except IntegrityError:
        session.rollback()
        logger.error(f"Failed to create user '{username}': Integrity error.")
        return jsonify({"message": "User already exists"}), 409
    finally:
        session.close()

@app.route('/users', methods=['GET'])
def get_users():
    session = Session()
    users = session.query(User).all()
    user_list = [{"username": user.username, "email": user.email} for user in users]
    logger.info(f"Fetched {len(user_list)} users.")
    session.close()
    
    return jsonify({"users": user_list}), 200

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    user_id = data.get('user_id')
    
    session = Session()
    task = Task(title=title, user_id=user_id)

    session.add(task)
    try:
        session.commit()
        logger.info(f"Task '{title}' created successfully.")
        return jsonify({"message": "Task created", "task": {"title": title}}), 201
    except IntegrityError:
        session.rollback()
        logger.error(f"Failed to create task '{title}': Integrity error.")
        return jsonify({"message": "Task creation failed"}), 409
    finally:
        session.close()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    session = Session()
    tasks = session.query(Task).all()
    task_list = [{"title": task.title, "status": task.status} for task in tasks]
    logger.info(f"Fetched {len(task_list)} tasks.")
    session.close()
    
    return jsonify({"tasks": task_list}), 200

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task_status(task_id):
    data = request.get_json()
    status = data.get('status')

    session = Session()
    task = session.query(Task).filter(Task.id == task_id).first()

    if task is None:
        logger.warning(f"Task {task_id} not found.")
        return jsonify({"message": "Task not found"}), 404

    task.status = status
    session.commit()
    logger.info(f"Task {task_id} status updated to '{status}'.")
    session.close()

    return jsonify({"message": "Task status updated"}), 200

@app.route('/performance_metrics', methods=['GET'])
def performance_metrics():
    # Dummy metrics for demonstration
    metrics = {
        "total_users": 1000,
        "active_tasks": 500,
        "request_latency": random.uniform(20, 100),  # Simulate latency
    }
    logger.info("Fetched performance metrics.")
    return jsonify(metrics), 200

if __name__ == "__main__":
    performance_tuning_query()  # Pre-load some data for testing
    app.run(host='0.0.0.0', port=5000)