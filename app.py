import os
import openai
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Fix the database URL to use the correct dialect
database_url = os.getenv('DATABASE_URL')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model
class BrandEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100), nullable=False)
    scores = db.Column(db.JSON, nullable=False)
    good_taste_score = db.Column(db.Float, nullable=False)
    gpt_evaluation = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create the database tables
with app.app_context():
    db.create_all()

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
    brand_evaluation = BrandEvaluation(
        brand=brand,
        category=category,
        subcategory=subcategory,
        scores=scores,
        good_taste_score=good_taste_score,
        gpt_evaluation=gpt_evaluation
    )
    db.session.add(brand_evaluation)
    db.session.commit()
    
    return jsonify({
        "brand": brand,
        "category": category,
        "subcategory": subcategory,
        "good_taste_score": good_taste_score,
        "scores": scores,
        "gpt_evaluation": gpt_evaluation
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
