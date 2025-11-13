import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score

np.random.seed(42)

def create_synthetic_dataset():
    """Create synthetic cattle health dataset"""
    n_samples = 200
    data = pd.DataFrame({
        'body_temperature': np.concatenate([
            np.random.normal(38.5, 0.5, 140),
            np.random.normal(40.0, 0.8, 60)
        ]),
        'breed_type': np.random.choice([0, 1], n_samples),
        'milk_production': np.concatenate([
            np.random.normal(20, 4, 140),
            np.random.normal(8, 3, 60)
        ]),
        'respiratory_rate': np.concatenate([
            np.random.normal(30, 5, 140),
            np.random.normal(45, 10, 60)
        ]),
        'walking_capacity': np.concatenate([
            np.random.normal(12000, 2000, 140),
            np.random.normal(6000, 3000, 60)
        ]),
        'heart_rate': np.concatenate([
            np.random.normal(60, 10, 140),
            np.random.normal(80, 15, 60)
        ]),
        'faecal_consistency': np.random.choice([0, 1, 2, 3, 4], n_samples, 
                                               p=[0.7, 0.1, 0.1, 0.05, 0.05])
    })
    
    # Determine health status
    conditions = (
        (data['body_temperature'] > 39.5) | 
        (data['milk_production'] < 10) | 
        (data['respiratory_rate'] > 40) | 
        (data['walking_capacity'] < 8000)
    )
    data['health_status'] = np.where(conditions, 1, 0)  # 1=unhealthy, 0=healthy
    
    return data

def train_and_save_model():
    """Train model and save to pickle file"""
    print("Training Cattle Health Model...")
    
    # Create dataset
    data = create_synthetic_dataset()
    
    # Prepare features
    feature_columns = [
        'body_temperature', 'breed_type', 'milk_production',
        'respiratory_rate', 'walking_capacity', 'heart_rate',
        'faecal_consistency'
    ]
    
    X = data[feature_columns]
    y = data['health_status']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=['Healthy', 'Unhealthy']))
    
    # Save model
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_columns': feature_columns
    }
    
    with open('cattle_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("\n Model saved as 'cattle_model.pkl'")
    print(" Ready to use with Flask backend!")

if __name__ == '__main__':
    train_and_save_model()