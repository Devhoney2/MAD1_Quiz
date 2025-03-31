from flask import Flask, render_template, redirect, url_for, flash, session, request
from models import db, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quizmo_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# database and admin user 
@app.before_first_request
def setup():

    db.create_all()

    admin = User.query.filter_by(username='custom_admin').first()
    if not admin:
        admin = User(
            username='custom_ admin',
            full_name='Custom Admin',
            is_admin=True
        )

        admin.set_password('custom_password')
        db.session.add(admin)
        db.session.commit()



# Checking admin
def is_admin():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return user and user.is_admin
    return False



# Index
@app.route('/')
def index():
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            
            return redirect(url_for('user_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')



# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob_str = request.form['dob']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            dob = None

        new_user = User(
            username=username,
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            is_admin=False
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')



# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('login'))




# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if not is_admin():
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('login'))
    subjects_count = Subject.query.count()
    chapters_count = Chapter.query.count()
    quizzes_count = Quiz.query.count()
    users_count = User.query.filter_by(is_admin=False).count()
    return render_template('admin_dashboard.html',
                           subjects_count=subjects_count,
                           chapters_count=chapters_count,
                           quizzes_count=quizzes_count,
                           users_count=users_count)

app.jinja_env.globals.update(is_admin=is_admin)


# Add subject
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if not is_admin():
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully')
        return redirect(url_for('subject_list'))
    return render_template('subject_form.html')

# Subject list
@app.route('/subject_list')
def subject_list():
    if not is_admin():
        return redirect(url_for('login'))
    subjects = Subject.query.all()
    return render_template('subject_list.html', subjects=subjects)

# Edit subject
@app.route('/edit_subject/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    if not is_admin():
        return redirect(url_for('login'))
    subject = Subject.query.get(id)
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully')
        return redirect(url_for('subject_list'))
    return render_template('subject_form.html', subject=subject)

# Delete subject 
@app.route('/delete_subject/<int:id>', methods=['POST'])
def delete_subject(id):
    if not is_admin():
        return redirect(url_for('login'))
    subject = Subject.query.get(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully')
    return redirect(url_for('subject_list'))



# Add chapter
@app.route('/add_chapter', methods=['GET', 'POST'])
def add_chapter():
    if not is_admin():
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        subject_id = request.form['subject_id']
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully')
        return redirect(url_for('chapter_list'))
    subjects = Subject.query.all()
    return render_template('chapter_form.html', subjects=subjects)

# Chapter list
@app.route('/chapter_list')
def chapter_list():
    if not is_admin():
        return redirect(url_for('login'))
    chapters = Chapter.query.all()
    return render_template('chapter_list.html', chapters=chapters)

# Edit chapter
@app.route('/edit_chapter/<int:id>', methods=['GET', 'POST'])
def edit_chapter(id):
    if not is_admin():
        return redirect(url_for('login'))
    chapter = Chapter.query.get(id)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        chapter.subject_id = request.form['subject_id']
        db.session.commit()
        flash('Chapter updated successfully')
        return redirect(url_for('chapter_list'))
    subjects = Subject.query.all()
    return render_template('chapter_form.html', chapter=chapter, subjects=subjects)



# Delete chapter
@app.route('/delete_chapter/<int:id>',methods=['POST'])
def delete_chapter(id):
    if not is_admin():
        return redirect(url_for('login'))
    chapter = Chapter.query.get(id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully')
    return redirect(url_for('chapter_list'))

# Add quiz
@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if not is_admin():
        return redirect(url_for('login'))
    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        date_str = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        remarks = request.form['remarks']
        date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
        quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration, remarks=remarks)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully')
        return redirect(url_for('quiz_list'))
    chapters = Chapter.query.all()
    return render_template('quiz_form.html', chapters=chapters)




# Quiz list
@app.route('/quiz_list')
def quiz_list():
    if not is_admin():
        return redirect(url_for('login'))
    quizzes = Quiz.query.all()
    return render_template('quiz_list.html', quizzes=quizzes)




# Edit quiz
@app.route('/edit_quiz/<int:id>', methods=['GET', 'POST'])
def edit_quiz(id):
    if not is_admin():
        return redirect(url_for('login'))
    quiz = Quiz.query.get(id)
    if request.method == 'POST':
        quiz.chapter_id = request.form['chapter_id']
        date_str = request.form['date_of_quiz']
        quiz.date_of_quiz = datetime.strptime(date_str, '%Y-%m-%d').date()
        quiz.time_duration = request.form['time_duration']
        quiz.remarks = request.form['remarks']
        db.session.commit()
        flash('Quiz updated successfully')
        return redirect(url_for('quiz_list'))
    chapters = Chapter.query.all()
    return render_template('quiz_form.html', quiz=quiz, chapters=chapters)


# Delete quiz
@app.route('/delete_quiz/<int:id>',methods=['POST'])
def delete_quiz(id):
    if not is_admin():
        return redirect(url_for('login'))
    quiz = Quiz.query.get(id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully')
    return redirect(url_for('quiz_list'))

# Add question
@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    if not is_admin():
        return redirect(url_for('login'))
    quiz = Quiz.query.get(quiz_id)
    if request.method == 'POST':
        question = Question(
            quiz_id=quiz_id,
            question_statement=request.form['question_statement'],
            option1=request.form['option1'],
            option2=request.form['option2'],
            option3=request.form['option3'],
            option4=request.form['option4'],
            correct_option=int(request.form['correct_option'])
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully')
        return redirect(url_for('question_list', quiz_id=quiz_id))
    return render_template('question_form.html', quiz=quiz)

# Question list
@app.route('/question_list/<int:quiz_id>')
def question_list(quiz_id):
    if not is_admin():
        return redirect(url_for('login'))
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('question_list.html', quiz=quiz, questions=questions)





# Edit question
@app.route('/edit_question/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    if not is_admin():
        return redirect(url_for('login'))
    question = Question.query.get(id)
    if request.method == 'POST':
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = int(request.form['correct_option'])
        db.session.commit()
        flash('Question updated successfully')
        return redirect(url_for('question_list', quiz_id=question.quiz_id))
    return render_template('question_form.html', question=question, quiz=question.quiz)


# Delete question
@app.route('/delete_question/<int:id>', methods=['POST'])
def delete_question(id):
    if not is_admin():
        return redirect(url_for('login'))
    question = Question.query.get(id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully')
    return redirect(url_for('question_list', quiz_id=quiz_id))

# User dashboard
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin_dashboard'))
    subjects = Subject.query.all()

    attempted_quizzes = Score.query.filter_by(user_id=user.id).all()

    return render_template('user_dashboard.html',
                           user=user,
                           subjects=subjects,
                           attempted_quizzes=attempted_quizzes)



# Chapters for user
@app.route('/chapters/<int:subject_id>')
def user_chapters(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    subject = Subject.query.get(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('chapters.html', subject=subject, chapters=chapters)

# Quizzes for users
@app.route('/quizzes/<int:chapter_id>')
def user_quizzes(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    chapter = Chapter.query.get(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('quizzes.html', chapter=chapter, quizzes=quizzes)



# Attempt quiz
@app.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if request.method == 'POST':
        score = 0
        total_questions = len(questions)
        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += 1
        new_score = Score(
            quiz_id=quiz_id,
            user_id=user_id,
            total_scored=score
        )
        db.session.add(new_score)
        db.session.commit()
        return redirect(url_for('quiz_result', score_id=new_score.id))
    return render_template('quiz_attempt.html', quiz=quiz, questions=questions)

# quiz result
@app.route('/quiz_result/<int:score_id>')
def quiz_result(score_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    score = Score.query.get(score_id)
    if score.user_id != session['user_id']:
        flash('Access denied')
        return redirect(url_for('user_dashboard'))
    quiz = score.quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    total_questions = len(questions)
    return render_template('quiz_result.html',
                           score=score,
                           quiz=quiz,
                           total_questions=total_questions)

# Manage users 
@app.route('/manage_users')
def manage_users():
    if not is_admin():
        return redirect(url_for('login'))
    users = User.query.filter_by(is_admin=False).all()
    return render_template('manage_users.html', users=users)



# Edit user (Admin only)
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if not is_admin():
        return redirect(url_for('login'))
    user = User.query.get(id)
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.qualification = request.form['qualification']
        user.dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        db.session.commit()
        flash('User updated successfully')
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', user=user)

# Delete user (Admin only)
@app.route('/delete_user/<int:id>',methods=['POST'])
def delete_user(id):
    if not is_admin():
        return redirect(url_for('login'))
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('manage_users'))

if __name__ == '__main__':
    app.run(debug=True)
