import os
from flask import Flask, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from extensions import db
from forms import GradeForm
from db_models import GradeRecord

# Загружаем переменные окружения из файла .env
load_dotenv()
app = Flask(__name__)

# Настройка SQLite (файл journal.db создастся в папке instance или в корне)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

db.init_app(app)

# Секретный ключ нужен для шифрования сессий и защиты форм (понадобится в Часе 3 и 4)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "<h1>Привет, Веб! Это мой журнал успеваемости.</h1>"


@app.route('/health')
def health_check():
    return "<h1>Приложение работает!</h1>"

@app.route('/add_grade', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    # debug=True автоматически перезагружает сервер при изменении кода
    app.run(debug=True)

