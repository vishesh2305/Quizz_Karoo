from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from extensions import db
from routes import auth
from models import User

app = Flask(__name__)


from config import Config
app.config.from_object(Config)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth, url_prefix="/auth")

@app.route("/")
def home():
    return redirect(url_for("auth.register"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))















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















if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
    app.run(debug=True)