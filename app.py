import os
import openai
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('path/to/your/firebase_credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define categories
categories = [
    "Cultural Sensitivity (CS)",
    "Aesthetic Appreciation (AA)",
    "Context Awareness (CA)",
    "Quality (Q)",
    "Originality (O)",
    "Emotional Resonance (ER)",
    "Functionality (F)",
    "Relative Taste Score (RTS)",
    "Staying Power (SP)",
    "Sustainability (S)",
    "Innovation (I)",
    "Safety (SF)",
    "Market Performance (MP)",
    "Customer Satisfaction (CS)"
]

@app.route('/')
def index():
    return render_template('index.html', categories=categories)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    scores = data['scores']
    brand = data['brand']
    category = data['category']
    subcategory = data['subcategory']
    good_taste_score = sum(scores) / len(scores)
    
    # Use OpenAI API to enhance evaluation (example)
    response = openai.Completion.create(
        engine="text-davinci-004",
        prompt=f"Evaluate the brand {brand} with scores {scores} in the context of good taste.",
        max_tokens=150
    )
    gpt_evaluation = response.choices[0].text.strip()
    
    # Capture data with timestamp
    timestamp = datetime.utcnow().isoformat()
    doc_ref = db.collection('brand_evaluations').document()
    doc_ref.set({
        'brand': brand,
        'category': category,
        'subcategory': subcategory,
        'scores': scores,
        'good_taste_score': good_taste_score,
        'timestamp': timestamp
    })
    
    return jsonify({
        "brand": brand,
        "category": category,
        "subcategory": subcategory,
        "good_taste_score": good_taste_score,
        "scores": scores,
        "gpt_evaluation": gpt_evaluation
    })

if __name__ == '__main__':
    app.run(debug=True)
