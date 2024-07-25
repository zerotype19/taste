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
    return render_template('index.html')

@app.route('/confirm', methods=['POST'])
def confirm():
    data = request.json
    brand = data['brand']
    
    # Use OpenAI API to confirm the brand category and subcategory
    response = openai.Completion.create(
        engine="text-davinci-004",
        prompt=f"Determine the category and subcategory for the brand {brand}.",
        max_tokens=50
    )
    gpt_response = response.choices[0].text.strip()
    
    # For simplicity, let's assume the response is in the format "Category: <category>, Subcategory: <subcategory>"
    category = gpt_response.split(',')[0].split(':')[1].strip()
    subcategory = gpt_response.split(',')[1].split(':')[1].strip()
    
    return jsonify({
        "brand": brand,
        "category": category,
        "subcategory": subcategory
    })

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    brand = data['brand']
    
    # Use OpenAI API to get evaluation scores
    response = openai.Completion.create(
        engine="text-davinci-004",
        prompt=f"Evaluate the brand {brand} on the following categories: {', '.join(categories)}. Provide scores between 0 and 10 for each category.",
        max_tokens=150
    )
    gpt_response = response.choices[0].text.strip()
    
    # For simplicity, let's assume the response is in the format "CS: 8, AA: 7, ..."
    scores = [int(score.split(':')[1].strip()) for score in gpt_response.split(',')]
    good_taste_score = sum(scores) / len(scores)
    
    # Capture data with timestamp
    brand_evaluation = BrandEvaluation(
        brand=brand,
        category=data['category'],
        subcategory=data['subcategory'],
        scores=scores,
        good_taste_score=good_taste_score,
        gpt_evaluation=gpt_response
    )
    db.session.add(brand_evaluation)
    db.session.commit()
    
    return jsonify({
        "brand": brand,
        "category": data['category'],
        "subcategory": data['subcategory'],
        "good_taste_score": good_taste_score,
        "scores": scores,
        "gpt_evaluation": gpt_response,
        "categories": categories
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
