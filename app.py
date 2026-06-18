import os
from flask import Flask, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from extensions import db
from db_models import GradeRecord, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import GradeForm, RegisterForm, LoginForm

# Загружаем переменные окружения из файла .env
load_dotenv()
app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Имя роута, куда кидать неавторизованных

# Настройка SQLite (файл journal.db создастся в папке instance или в корне)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

db.init_app(app)

# Секретный ключ нужен для шифрования сессий и защиты форм (понадобится в Часе 3 и 4)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()



@app.route('/')
def home():
    return "<h1>Привет, Веб! Это мой журнал успеваемости.</h1>"


@app.route('/health')
def health_check():
    return "<h1>Приложение работает!</h1>"


@app.route('/add_grade', methods=['GET', 'POST'])
@login_required
def add_grade():
    form = GradeForm()
    # validate_on_submit() проверяет, что это POST-запрос И все валидаторы пройдены
    if form.validate_on_submit():
        new_grade = GradeRecord(
            student_name=form.student_name.data,
            subject=form.subject.data,
            work_type=form.work_type.data,
            score=form.score.data,
            comment=form.comment.data,
            date=form.date.data
        )
        db.session.add(new_grade)
        db.session.commit()
        flash('Оценка успешно добавлена!', 'success')
        return redirect(url_for('add_grade'))
    return render_template('add_grade.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.', 'danger')
            return redirect(url_for('register'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна. Теперь можно войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли.', 'success')
            return redirect(url_for('add_grade'))
        flash('Неверное имя пользователя или пароль.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

if __name__ == '__main__':
    # debug=True автоматически перезагружает сервер при изменении кода
    app.run(debug=True)
