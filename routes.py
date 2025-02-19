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
        category = request.form.get('category')
        difficulty = request.form.get('difficulty')

        # 1. Create the Quiz itself
        quiz = Quiz(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            created_by=current_user.id
        )
        db.session.add(quiz)
        db.session.commit()

        # 2. Capture all 'questions[]' form inputs
        questions = request.form.getlist('questions[]')

        # Loop over each question
        for q_index, question_text in enumerate(questions):
            question = Question(text=question_text, quiz_id=quiz.id)
            db.session.add(question)
            db.session.commit()  # commit so the question has an ID for linking options

            # 3. For each question, get the corresponding options and the correct index
            options = request.form.getlist(f'options_{q_index}[]')
            correct_index = request.form.get(f'correct_{q_index}')  # e.g. "0" or "1" etc.

            # 4. Create Option objects
            for i, option_text in enumerate(options):
                is_correct = (str(i) == correct_index)
                option = Option(
                    text=option_text, 
                    is_correct=is_correct, 
                    question_id=question.id
                )
                db.session.add(option)

        db.session.commit()
        flash('Quiz created successfully with questions and options!', 'success')
        return redirect(url_for('auth.quizzes'))

    return render_template('quiz_create.html')




@auth.route('/quizzes', methods=['GET'])
@login_required
def quizzes():
    # Get filters
    category = request.args.get('category', '').strip()
    difficulty = request.args.get('difficulty', '').strip()

    # Start with all quizzes
    query = Quiz.query

    if category:
        query = query.filter_by(category=category)

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    all_quizzes = query.all()

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
    results = []

    for question in questions:
        selected_option_id = request.form.get(f'question_{question.id}')
        selected_option = Option.query.get(int(selected_option_id)) if selected_option_id else None
        correct_option = next((option for option in question.options if option.is_correct), None)

        # Track result per question
        results.append({
            'question': question.text,
            'selected_option': selected_option.text if selected_option else "Not Answered",
            'correct_option': correct_option.text
        })

        # Calculate score
        if selected_option and selected_option.is_correct:
            score += 1

    return render_template(
        'view_quiz.html',
        quiz=quiz,
        score=score,
        total=len(questions),
        results=results,
        show_results=True  # This flag will be used in the template
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



@auth.route('/aboutus')
def adminPage():
    return render_template("./aboutus.html")





@auth.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    new_username = request.form.get('username')

    if new_username:
        current_user.username = new_username
        db.session.commit()
        flash('Profile updated successfully!', 'success')

    return redirect(url_for('auth.profile'))






@auth.route('/educational_quiz')
def educational_quiz():
    return render_template('Educational_quiz_container/edu_quiz_list.html')

@auth.route('/food_quiz')
def food_quiz():
    return render_template('Food_Quiz_Container/food_quiz_list.html')

@auth.route('/political_quiz')
def political_quiz():
    return render_template('Political_Quiz_Container/political_quiz_list.html')

@auth.route('/geographical_quiz')
def geographical_quiz():
    return render_template('Geographical_Quiz_Container/geographical_quiz_list.html')

@auth.route('/currentaffairs_quiz')
def currentaffairs_quiz():
    return render_template('CurrentAffairs_Quiz_Container/currentAffairs_quiz_list.html')

@auth.route('/historical_quiz')
def historical_quiz():
    return render_template('Historical_Quiz_Container/historical_quiz_list.html')

@auth.route('/health_quiz')
def health_quiz():
    return render_template('Health_Quiz_Container/health_quiz_list.html')

@auth.route('/scientific_quiz')
def scientific_quiz():
    return render_template('Scientific_Quiz_Container/science_quiz_list.html')

@auth.route('/household_quiz')
def household_quiz():
    return render_template('Household_Quiz_Container/household_quiz_list.html')

@auth.route('/gk_quiz')
def gk_quiz():
    return render_template('GeneralKnowledge_Quiz_Container/gk_quiz_list.html')



@auth.route('/search', methods=['GET'])
def search_quizzes():
    query = request.args.get('q', '').strip()

    if query:
        quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
    else:
        quizzes = Quiz.query.all()

    return render_template('search_results.html', quizzes=quizzes, query=query)









@auth.route("/ca_quiz_1")
def ca_quiz_1():
    return render_template("CurrentAffairs_Quiz_Container/currentaffair_quizzes/ca_quiz_1.html")

@auth.route("/ca_quiz_2")
def ca_quiz_2():
    return render_template("CurrentAffairs_Quiz_Container/currentaffair_quizzes/ca_quiz_2.html")
@auth.route("/ca_quiz_3")
def ca_quiz_3():
    return render_template("CurrentAffairs_Quiz_Container/currentaffair_quizzes/ca_quiz_3.html")

@auth.route("/ca_quiz_4")
def ca_quiz_4():
    return render_template("CurrentAffairs_Quiz_Container/currentaffair_quizzes/ca_quiz_4.html")
@auth.route("/ca_quiz_5")
def ca_quiz_5():
    return render_template("CurrentAffairs_Quiz_Container/currentaffair_quizzes/ca_quiz_5.html")

@auth.route("/ca_quiz_6")
def ca_quiz_6():
    return render_template("CurrentAffairs_Quiz_Container/currentaffair_quizzes/ca_quiz_6.html")
@auth.route("/ca_quiz_7")
def ca_quiz_7():
    return render_template("CurrentAffairs_Quiz_Container/currentaffair_quizzes/ca_quiz_7.html")









@auth.route("/edu_quiz_1")
def edu_quiz_1():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_1.html")

@auth.route("/edu_quiz_2")
def edu_quiz_2():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_2.html")

@auth.route("/edu_quiz_3")
def edu_quiz_3():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_3.html")

@auth.route("/edu_quiz_4")
def edu_quiz_4():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_4.html")

@auth.route("/edu_quiz_5")
def edu_quiz_5():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_5.html")

@auth.route("/edu_quiz_6")
def edu_quiz_6():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_6.html")

@auth.route("/edu_quiz_7")
def edu_quiz_7():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_7.html")

@auth.route("/edu_quiz_8")
def edu_quiz_8():
    return render_template("Educational_quiz_container/Educational_Quizzes/edu_quiz_8.html")




@auth.route('/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('view_quiz.html', quiz=quiz)
