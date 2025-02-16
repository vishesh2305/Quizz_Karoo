from flask import Blueprint, flash, redirect, url_for, render_template, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User
from models import Quiz
from forms import RegistrationForm, LoginForm
from models import Quiz, User, Question, Option


auth = Blueprint("auth", __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        current_app.logger.info("Form validation successful.")

        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('auth.login'))

        # Hash password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Create new user (Default: Not an Admin)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=False)

        try:
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info("User successfully added to the database.")

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {e}")
            flash("An error occurred. Please try again.", "danger")

    return render_template('register.html', form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            flash("You have been logged in!", "success")

            # Redirect to next page (if any) or dashboard
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("auth.dashboard"))
        else:
            flash("Login unsuccessful. Check email and password.", "danger")

    return render_template("login.html", form=form)



# @auth.route('/quiz/<int:quiz_id>')
# @login_required
# def view_quiz(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     return render_template('view_quiz.html', quiz=quiz)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth.route("/dashboard")
@login_required
def dashboard():
    quizzes= Quiz.query.all()
    return render_template("dashboard.html")


@auth.route('/create-quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if not current_user.is_admin:
        flash("You are not authorized to create quizzes.", "danger")
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        # Create the Quiz
        quiz = Quiz(title=title, description=description, created_by=current_user.id)
        db.session.add(quiz)
        db.session.commit()

        # Handle Questions & Options
        questions = request.form.getlist('questions[]')

        for q_index, question_text in enumerate(questions):
            question = Question(text=question_text, quiz_id=quiz.id)
            db.session.add(question)
            db.session.commit()

            # Get options and correct answer for this question
            options = request.form.getlist(f'options_{q_index}[]')
            correct_index = request.form.get(f'correct_{q_index}')  # This is a string

            for i, option_text in enumerate(options):
                is_correct = str(i) == correct_index
                option = Option(text=option_text, is_correct=is_correct, question_id=question.id)
                db.session.add(option)

        db.session.commit()

        flash('Quiz created successfully with questions and options!', 'success')
        return redirect(url_for('auth.quizzes'))

    return render_template('quiz_create.html')






@auth.route('/quizzes')
@login_required
def quizzes():
    all_quizzes=Quiz.query.all()
    return render_template('quizzes.html', quizzes=all_quizzes)






@auth.route('/edit-quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Optional: Only let admins edit quizzes (Optional, if you want to restrict this)
    if not current_user.is_admin:
        flash("You are not authorized to edit quizzes.", "danger")
        return redirect(url_for('auth.quizzes'))

    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.description = request.form.get('description')
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('auth.quizzes'))

    return render_template('edit_quiz.html', quiz=quiz)






@auth.route('/delete-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Optional: Only let admins delete quizzes
    if not current_user.is_admin:
        flash("You are not authorized to delete quizzes.", "danger")
        return redirect(url_for('auth.quizzes'))

    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('auth.quizzes'))




@auth.route('/submit-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    score = 0

    # Process each question
    for question in questions:
        selected_option_id = request.form.get(f'question_{question.id}')

        # If no option is selected for a question, skip it
        if not selected_option_id:
            continue

        selected_option = Option.query.get(int(selected_option_id))

        # Check if the selected option is correct
        if selected_option and selected_option.is_correct:
            score += 1

    # Fetch all quizzes for displaying the page
    quizzes = Quiz.query.all()

    return render_template(
        'quizzes.html',
        quizzes=quizzes,
        quiz_result_id=quiz.id,
        quiz_score=score,
        quiz_total=len(questions)
    )



@auth.route('/profile')
@login_required
def profile():
    user_quizzes = current_user.quizzes  # From the relationship in models.py
    return render_template('profile_page.html', user_quizzes=user_quizzes)



@auth.route('/quiz_list_pages')
@login_required
def edu_quiz_list():
    return render_template('./quiz_list_pages.html')




@auth.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    new_username = request.form.get('username')

    if new_username:
        current_user.username = new_username
        db.session.commit()
        flash('Profile updated successfully!', 'success')

    return redirect(url_for('auth.profile'))

