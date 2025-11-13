from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# POE API Configuration
POE_API_KEY = "UDPvORBFXqUCNrQlE-_Tb0a4JVbCoDLCKTWLNtj5Pbw"
POE_API_URL = "https://api.poe.com/v1/chat/completions"
POE_MODEL = "Grok-4"

# Load the trained model
try:
    with open('cattle_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    predictor = model_data['model']
    scaler = model_data['scaler']
    feature_columns = model_data['feature_columns']
    print("✅ Model loaded successfully")
except:
    predictor = None
    scaler = None
    feature_columns = None
    print("⚠️ Model not found. Run model.py first to train and save the model.")

def query_poe_api(user_message, system_prompt=None):
    """Query Poe API for AI responses"""
    if not POE_API_KEY:
        return "API key not configured"
    
    if system_prompt is None:
        system_prompt = (
            "You are a practical cattle health assistant for African farmers. "
            "Give concise, actionable advice in 2-3 sentences. Use simple language. "
            "Do not prescribe medications. Advise contacting a veterinarian if serious."
        )
    
    headers = {
        "Authorization": f"Bearer {POE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": POE_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    try:
        response = requests.post(POE_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return jsonify({"message": "Cattle Health API is running", "status": "ok"})

@app.route('/api/health-check', methods=['POST'])
def health_check():
    """Endpoint for cattle health prediction"""
    try:
        data = request.json
        
        # Extract features
        features = {
            'body_temperature': float(data.get('temperature', 38.5)),
            'milk_production': float(data.get('milk', 15)),
            'respiratory_rate': float(data.get('respiratory', 30)),
            'heart_rate': float(data.get('heart_rate', 60)),
            'walking_capacity': float(data.get('walking', 12000)),
            'breed_type': int(data.get('breed', 0)),
            'faecal_consistency': int(data.get('faecal', 1))
        }
        
        # Prepare features for prediction
        feature_array = np.array([[
            features['body_temperature'],
            features['breed_type'],
            features['milk_production'],
            features['respiratory_rate'],
            features['walking_capacity'],
            features['heart_rate'],
            features['faecal_consistency']
        ]])
        
        # Scale features
        feature_scaled = scaler.transform(feature_array)
        
        # Make prediction
        prediction = predictor.predict(feature_scaled)[0]
        probability = predictor.predict_proba(feature_scaled)[0]
        confidence = float(max(probability))
        
        health_status = "healthy" if prediction == 0 else "unhealthy"
        
        # Generate AI recommendations
        context = f"""Health Status: {health_status.upper()} (Confidence: {confidence:.1%})
Measurements:
- Body Temperature: {features['body_temperature']}°C
- Milk Production: {features['milk_production']} liters
- Respiratory Rate: {features['respiratory_rate']} breaths/min
- Heart Rate: {features['heart_rate']} bpm
- Walking Capacity: {features['walking_capacity']} steps

Provide practical advice for this cattle."""
        
        ai_recommendations = query_poe_api(context)
        
        return jsonify({
            'success': True,
            'health_status': health_status,
            'confidence': confidence,
            'recommendations': ai_recommendations,
            'features': features
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint for chatbot conversations - CATTLE ONLY"""
    try:
        data = request.json
        user_message = data.get('message', '')
        farmer_name = data.get('farmer_name', 'Cattle Farmer')
        farm_location = data.get('farm_location', 'Unknown')

        # Enhanced cattle-only system prompt
        cattle_system_prompt = (
            "You are a specialized CATTLE HEALTH AND MANAGEMENT assistant. "
            "STRICTLY focus ONLY on topics related to cattle (cows, bulls, calves). "
            "ALLOWED TOPICS: "
            "- Cattle health, diseases, symptoms "
            "- Milk production and dairy cattle management "
            "- Beef cattle breeding and care "
            "- Calf nutrition and weaning "
            "- Cattle feeding, pasture, fodder "
            "- Cattle shelter, barn management "
            "- Cattle behavior and welfare "
            "- Cattle vaccination and preventive care "
            "- Cattle reproduction and breeding "
            "PROHIBITED TOPICS: "
            "- Other animals (sheep, goats, chickens, pets) "
            "- Crop farming or agriculture "
            "- Human health or medicine "
            "- Non-cattle veterinary topics "
            "- General farming equipment "
            "If asked about non-cattle topics, respond: "
            "'I specialize exclusively in cattle health and management. Please ask about cattle-related topics.' "
            "Keep responses practical, 2-3 sentences maximum for African cattle farmers."
        )

        context_message = f"Cattle farmer {farmer_name} from {farm_location} asks: {user_message}"
        
        ai_response = query_poe_api(context_message, cattle_system_prompt)
        
        return jsonify({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/greeting', methods=['POST'])
def greeting():
    """Generate personalized greeting"""
    try:
        data = request.json
        farmer_name = data.get('farmer_name', 'Farmer')
        farm_location = data.get('farm_location', 'Unknown')
        
        greeting_prompt = f"Greet {farmer_name} from {farm_location} warmly as a cattle health assistant. Ask how you can help with their cattle today. Keep it brief and friendly."
        ai_greeting = query_poe_api(greeting_prompt)
        
        return jsonify({
            'success': True,
            'greeting': ai_greeting
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)