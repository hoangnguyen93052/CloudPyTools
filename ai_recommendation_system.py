import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Set up Flask application
app = Flask(__name__)
CORS(app)

# Load dataset
def load_data():
    # Example dataset
    data = {
        'user_id': [1, 1, 2, 2, 3, 3, 4, 4, 5],
        'item_id': [1, 2, 2, 3, 1, 3, 1, 4, 5],
        'rating': [5, 4, 3, 5, 2, 4, 4, 5, 5]
    }
    df = pd.DataFrame(data)
    return df

# Create a user-item matrix
def create_user_item_matrix(df):
    user_item_matrix = df.pivot(index='user_id', columns='item_id', values='rating').fillna(0)
    return user_item_matrix

# Compute cosine similarity
def compute_cosine_similarity(user_item_matrix):
    cosine_sim = cosine_similarity(user_item_matrix)
    return cosine_sim

# Get recommendations based on user similarity
def get_recommendations(user_id, user_item_matrix, cosine_sim):
    user_idx = user_id - 1  # Assuming user_ids start from 1
    similar_users = list(enumerate(cosine_sim[user_idx]))
    similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)[1:6]  # Top 5 similar users
    similar_user_indices = [i[0] for i in similar_users]
    
    user_item_matrix_t = user_item_matrix.T
    recommended_items = pd.Series()
    
    for idx in similar_user_indices:
        recommended_items = recommended_items.append(user_item_matrix_t.iloc[:, idx])
    
    recommended_items = recommended_items.groupby(recommended_items.index).mean().sort_values(ascending=False)
    return recommended_items.index[:5].tolist()  # Return top 5 item IDs

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_id = data['user_id']
    
    df = load_data()
    user_item_matrix = create_user_item_matrix(df)
    cosine_sim = compute_cosine_similarity(user_item_matrix.values)
    
    recommendations = get_recommendations(user_id, user_item_matrix, cosine_sim)
    return jsonify({'recommendations': recommendations})

@app.route('/data', methods=['GET'])
def get_data():
    df = load_data()
    return df.to_json(orient="records")

if __name__ == '__main__':
    app.run(debug=True)