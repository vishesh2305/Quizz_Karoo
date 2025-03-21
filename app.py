from flask import Flask, redirect, url_for, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user
from extensions import db
from routes import auth
from models import User, Quiz, Question, Option
from dotenv import load_dotenv
import os
import google.generativeai as genai
from config import Config
import json  # Import the json module

load_dotenv()

app = Flask(__name__)

# Load API key from environment variable
app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')


# Configure app with config class (Important!)
app.config.from_object(Config)  # Assuming Config is in config.py

# Database Configuration (Important!)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
app.register_blueprint(auth, url_prefix="/auth")


# --- User Loader & Routes ---
@app.route("/")
def home():
    return redirect(url_for("auth.register"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Gemini Quiz Generation Function ---
def generate_quiz(topic=""):
    """Generates a quiz using Gemini API."""
    # Ensure the API key is set
    if not app.config.get('GEMINI_API_KEY'):
        print("Error: Gemini API key not found in configuration.")
        return None

    try:
        genai.configure(api_key=app.config['GEMINI_API_KEY'])
        model = genai.GenerativeModel('gemini-1.5-pro') # Use the correct model name
        prompt = f"""
        Generate a JSON object representing a multiple-choice quiz based on the topic '{topic}'. If the topic is empty, choose any general topic.
        The quiz should have:
        - title: A short quiz title.
        - description: A brief description.
        - category: Choose from ['Educational', 'Food', 'Political', 'Geographical', 'Current Affairs', 'Historical', 'Health', 'Scientific', 'Household', 'General Knowledge'].
        - difficulty: Choose from ['Easy', 'Medium', 'Hard'].
        - questions: A list of exactly 10 questions. Each question should have:
            - text: The question text.
            - options: A list of 4 options.
            - correct_option_index: Index (0, 1, 2, or 3) indicating the correct option.
        Respond with ONLY the JSON object. No explanations or preamble.
        """
        response = model.generate_content(prompt)

        response_text = response.text.strip().strip("```json").strip("```")  # Correctly strip
        quiz_data = json.loads(response_text)
        return quiz_data

    except json.JSONDecodeError as e:
        print("JSON Parsing Failed:", e)
        print("Response from Gemini was:", response.text)
        return None
    except Exception as e:
        print(f"An error occurred during quiz generation: {e}")
        return None


# --- API Routes ---

@app.route('/load_more_quizzes', methods=['GET'])
def load_more_quizzes():
    """Loads more quizzes (not fully implemented, but a good starting point)."""
    quiz_content = generate_quiz()
    if quiz_content:
        return jsonify({'quizzes': [quiz_content]})  # Return as a list for consistency
    else:
        return jsonify({'error': 'Failed to generate quiz'}), 500


@app.route('/generate_quiz_and_store', methods=['POST'])
@login_required
def generate_quiz_and_store():
    """Generates a quiz based on a topic, stores it in the database."""
    query_topic = request.json.get('topic', '')

    quiz_data = generate_quiz(topic=query_topic)

    if not quiz_data:
        return jsonify({'error': 'Failed to generate quiz'}), 500

    try:
        # Create Quiz record
        quiz = Quiz(
            title=quiz_data['title'],
            description=quiz_data['description'],
            category=quiz_data['category'],
            difficulty=quiz_data['difficulty'],
            created_by=current_user.id
        )
        db.session.add(quiz)
        db.session.commit()

        # Create Question and Option records
        for q in quiz_data['questions']:
            question = Question(text=q['text'], quiz_id=quiz.id)
            db.session.add(question)
            db.session.commit()

            for i, option_text in enumerate(q['options']):
                is_correct = i == q['correct_option_index']
                option = Option(text=option_text, is_correct=is_correct, question_id=question.id)
                db.session.add(option)

        db.session.commit()
        return jsonify({'message': 'Quiz generated and stored successfully!', 'quiz_id': quiz.id})

    except Exception as e:
        db.session.rollback()  # Rollback in case of errors during database operations
        print(f"Database error: {e}")
        return jsonify({'error': 'Failed to store quiz in database'}), 500


# --- Template Routes (example) ---
@app.route("/educational-quizzes")
def educational_quizzes():
    return render_template("Educational_quiz_container/edu_quiz_list.html")

@app.route("/current-affairs-quizzes")
def current_affairs_quizzes():
    return render_template("CurrentAffairs_Quiz_Container/currentAffairs_quiz_list.html")

@app.route("/food-quizzes")
def food_quizzes():
    return render_template("Food_Quiz_Container/food_quiz_list.html")

@app.route("/general_knowledge_quizzes")
def general_knowledge_quizzes():
    return render_template("GeneralKnowledge_Quiz_Container/gk_quiz_list.html")

@app.route("/geographical_quizzes")
def geographical_quizzes():
    return render_template("Geographical_Quiz_Container/geographical_quiz_list.html")

@app.route("/health_quizzes")
def health_quizzes():
    return render_template("Health_Quiz_Container/health_quiz_list.html")

@app.route("/historical_quizzes")
def historical_quizzes():
    return render_template("Historical_Quiz_Container/historical_quiz_list.html")

@app.route("/political_quizzes")
def political_quizzes():
    return render_template("Political_Quiz_Container/political_quiz_list.html")

@app.route("/household_quizzes")
def household_quizzes():
    return render_template("Household_Quiz_Container/household_quiz_list.html")

@app.route("/scientific_quizzes")
def scientific_quizzes():
    return render_template("Scientific_Quiz_Container/science_quiz_list.html")


# --- Run the app ---
if __name__ == "__main__":
    port= int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
    app.run(debug=True)
