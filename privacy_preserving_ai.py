import numpy as np
import random
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import json
import pickle

# Function to simulate data generation for clients
def generate_data(num_samples=1000, num_features=20, num_classes=2):
    X, y = make_classification(n_samples=num_samples, n_features=num_features,
                               n_classes=num_classes, random_state=42)
    return X, y

# Function to split data into client datasets
def split_data(X, y, num_clients=5):
    client_data = {}
    for client_id in range(num_clients):
        client_samples = X.shape[0] // num_clients
        start = client_samples * client_id
        end = client_samples * (client_id + 1)
        client_data[client_id] = (X[start:end], y[start:end])
    return client_data

# Differential Privacy - Laplace Noise
def add_laplace_noise(value, sensitivity=1.0, epsilon=0.1):
    noise = np.random.laplace(0, sensitivity/epsilon)
    return value + noise

# Function for privacy-preserving model training on client data
def train_model(client_data):
    models = {}
    for client_id, (X, y) in client_data.items():
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        models[client_id] = model
    return models

# Function to aggregate models using averaging of weights
def aggregate_models(models):
    avg_model = RandomForestClassifier(n_estimators=100, random_state=42)
    avg_weights = None
    num_clients = len(models)

    for model in models.values():
        if avg_weights is None:
            avg_weights = model.estimators_
        else:
            for i in range(len(avg_weights)):
                avg_weights[i] += model.estimators_[i]
    
    avg_weights = [weights / num_clients for weights in avg_weights]
    avg_model.estimators_ = avg_weights
    return avg_model

# Function to evaluate model's accuracy
def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    return accuracy

# Simulating the federated learning process
def federated_learning(num_clients=5, num_samples=1000, test_size=0.2):
    # Generate and split data
    X, y = generate_data(num_samples=num_samples)
    client_data = split_data(X, y, num_clients)

    # Train models on client data
    models = train_model(client_data)

    # Aggregate models
    aggregated_model = aggregate_models(models)

    # Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Evaluate the aggregated model
    accuracy = evaluate_model(aggregated_model, X_test, y_test)
    print(f"Model Accuracy: {accuracy:.2f}")

# Save model to file
def save_model(model, filename='aggregated_model.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(model, f)

# Load model from file
def load_model(filename='aggregated_model.pkl'):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# Main execution point
if __name__ == "__main__":
    num_clients = 5
    num_samples = 1000
    
    federated_learning(num_clients=num_clients, num_samples=num_samples)
    
    # Save the aggregated model
    aggregated_model = load_model()
    save_model(aggregated_model)
    
    # Add differential privacy noise to model predictions (for demonstration)
    noise_added_accuracy = add_laplace_noise(0.90)
    print(f"Accuracy with Differential Privacy Noise: {noise_added_accuracy:.2f}")
    
    # Log final model accuracy and parameters
    model_params = {
        "num_clients": num_clients,
        "num_samples": num_samples,
        "accuracy": noise_added_accuracy
    }
    
    with open('model_log.json', 'w') as log_file:
        json.dump(model_params, log_file)

# Code to visualize client data distribution (could be developed further)
import matplotlib.pyplot as plt

def visualize_client_data_distribution(client_data):
    client_ids = list(client_data.keys())
    total_samples = [client_data[client_id][0].shape[0] for client_id in client_ids]
    
    plt.bar(client_ids, total_samples)
    plt.xlabel('Client ID')
    plt.ylabel('Number of Samples')
    plt.title('Client Data Distribution')
    plt.show()

# Uncomment to visualize the data distribution
# visualize_client_data_distribution(client_data)