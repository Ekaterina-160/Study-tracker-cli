# 📚 Этап 2: Flask, База Данных и Аутентификация

**🎯 Цель этапа:** Перенести логику из консоли в веб-интерфейс, понять цикл HTTP-запроса, освоить ORM (SQLAlchemy) и базовую веб-безопасность (аутентификация, защита форм).  
**⏱️ Время:** 4 часа (self-paced).  
**🛠️ Стек:** `Flask`, `Flask-SQLAlchemy`, `Flask-WTF`, `Flask-Login`, `python-dotenv`, `SQLite`.  
**📌 Предварительные условия:** Завершён Этап 1 (CLI, ООП, JSON, тесты, чистая история Git).

---

## ⏱️ Час 1: Введение в веб и настройка Flask

### 🧠 Концепции для понимания
1. **Клиент-серверная архитектура:** Чем веб отличается от CLI? Браузер (клиент) отправляет HTTP-запрос → Сервер (наш Python-код) его обрабатывает → Возвращает HTTP-ответ (обычно HTML или JSON).
2. **Stateless (отсутствие состояния):** Сервер по умолчанию "забывает" клиента сразу после отправки ответа. Каждый запрос независим. Это ключевая причина, почему нам позже понадобятся сессии и куки.
3. **Маршрутизация (Routing):** Как конкретный URL (например, `/add_grade`) превращается в вызов конкретной Python-функции.

### 💻 Практика
1. Создай новую ветку для фичи:
   ```bash
   git checkout -b feat/flask-setup
   
2. Обнови зависимости (добавь в requirements.txt или pyproject.toml и установи):
	```bash
	pip install flask python-dotenv
	
3. Создай файл .env в корне проекта. Важно: сразу добавь .env в .gitignore, чтобы секретные ключи не ушли в GitHub!
	```bash
	FLASK_APP=app.py
	FLASK_DEBUG=1
	SECRET_KEY=super_secret_dev_key_change_me_later
	
4. Создай файл app.py с минимальным приложением:
    ```python
    import os
    from flask import Flask
    from dotenv import load_dotenv

    # Загружаем переменные окружения из файла .env
    load_dotenv()

    app = Flask(__name__)
    # Секретный ключ нужен для шифрования сессий и защиты форм (понадобится в Часе 3 и 4)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    @app.route('/')
    def home():
        return "<h1>Привет, Веб! Это мой журнал успеваемости.</h1>"

    if __name__ == '__main__':
        # debug=True автоматически перезагружает сервер при изменении кода
        app.run(debug=True)

5. Запусти приложение: flask run (или python app.py) и открой в браузере http://127.0.0.1:5000.

✅ Чек-поинт: Коммит feat: init flask app with dotenv and basic route.

⏱️ Час 2: SQLAlchemy и миграция с JSON на SQLite
🧠 Концепции для понимания
1. Что такое ORM (Object-Relational Mapping)? Это мост между Python и базой данных. Мы работаем с привычными классами и объектами, а ORM (SQLAlchemy) автоматически превращает их в SQL-запросы и таблицы. Класс = Таблица, Атрибут = Колонка, Экземпляр класса = Строка в таблице.
2. Почему SQLite? Это идеальная база данных для разработки и небольших проектов. Она не требует установки отдельного сервера (как PostgreSQL), а хранит все данные в одном обычном файле (journal.db) прямо в папке проекта.
3. Контекст приложения (Application Context): В Flask некоторые операции (например, создание таблиц) требуют явного указания, к какому приложению они относятся, через with app.app_context():.
💻 Практика
Установи ORM-библиотеку:
    ```bash
    pip install flask-sqlalchemy

2. Обнови app.py, добавив инициализацию БД:
    ```python
    from flask_sqlalchemy import SQLAlchemy

    # Настройка SQLite (файл journal.db создастся в папке instance или в корне)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///journal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)

3. Создай файл db_models.py и перенеси туда адаптированные модели (старый models.py пока не удаляй, оставь для сравнения):
    ```python
    from datetime import datetime
    from app import db # Импортируем объект db из app.py

    class GradeRecord(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        student_name = db.Column(db.String(100), nullable=False)
        subject = db.Column(db.String(50), nullable=False)
        score = db.Column(db.Integer, nullable=False)
        date = db.Column(db.Date, default=datetime.utcnow)
        work_type = db.Column(db.String(50))
        comment = db.Column(db.Text)

    class StudySession(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        student_name = db.Column(db.String(100), nullable=False)
        subject = db.Column(db.String(50), nullable=False)
        topic = db.Column(db.String(100))
        duration_min = db.Column(db.Integer, nullable=False)
        date = db.Column(db.Date, default=datetime.utcnow)
        notes = db.Column(db.Text)

4. Создай таблицы в БД. Для этого открой интерактивную консоль Python в терминале:

    ```bash
    python
    
И выполни там:

    ```python
    from app import app, db
    with app.app_context():
        db.create_all()
    print("Таблицы созданы!")
    exit()
	
✅ Чек-поинт: Коммит feat: add sqlalchemy models and sqlite configuration. Убедись, что файл journal.db (или папка instance/) добавлен в .gitignore.

⏱️ Час 3: Формы и безопасность (Flask-WTF)
🧠 Концепции для понимания
1. GET vs POST: Почему данные формы должны отправляться через POST? GET помещает данные прямо в URL (например, ?score=100), что плохо для приватности и имеет лимит длины. POST передает данные в "теле" запроса, что безопаснее.
2. CSRF (Cross-Site Request Forgery): Представь, что ты залогинена на своем сайте. Злой сайт показывает тебе картинку, которая на самом деле является скрытой формой, отправляющей запрос на удаление твоего аккаунта. CSRF-токен — это уникальное секретное "рукопожатие", которое генерирует наш сервер и которое доказывает, что форму отправила именно наша страница, а не чужая.
3. Валидация на сервере: Никогда не доверяй данным от клиента (браузера). Проверять типы и обязательность полей нужно всегда на стороне Python, даже если есть проверка в HTML.
💻 Практика
1. Установи библиотеку для форм:
    ```bash
    pip install flask-wtf
2. Создай файл forms.py:
    ```python
    from flask_wtf import FlaskForm
    from wtforms import StringField, IntegerField, DateField, SubmitField
    from wtforms.validators import DataRequired, NumberRange

    class GradeForm(FlaskForm):
        student_name = StringField('Имя ученика', validators=[DataRequired()])
        subject = StringField('Предмет', validators=[DataRequired()])
        score = IntegerField('Балл', validators=[DataRequired(), NumberRange(min=1, max=100)])
        date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
        submit = SubmitField('Сохранить оценку')
3. Создай папку templates и в ней файл add_grade.html:
    ```html
    <!DOCTYPE html>
    <html>
    <head><title>Добавить оценку</title></head>
    <body>
        <h2>Добавить новую оценку</h2>
        <!-- form.hidden_tag() автоматически добавляет тот самый CSRF-токен -->
        <form method="POST">
            {{ form.hidden_tag() }}
            <p>
                {{ form.student_name.label }}<br>
                {{ form.student_name(size=32) }}
                {% for error in form.student_name.errors %}
                    <span style="color: red;">[{{ error }}]</span>
                {% endfor %}
            </p>
            <p>
                {{ form.subject.label }}<br>
                {{ form.subject(size=32) }}
            </p>
            <p>
                {{ form.score.label }}<br>
                {{ form.score() }}
            </p>
            <p>
                {{ form.date.label }}<br>
                {{ form.date() }}
            </p>
            <p>{{ form.submit() }}</p>
        </form>
    </body>
    </html>
4. Добавь роут в app.py:
    ```python
    from forms import GradeForm
    from db_models import GradeRecord
    from flask import render_template, redirect, url_for, flash

    @app.route('/add_grade', methods=['GET', 'POST'])
    def add_grade():
        form = GradeForm()
        # validate_on_submit() проверяет, что это POST-запрос И все валидаторы пройдены
        if form.validate_on_submit():
            new_grade = GradeRecord(
                student_name=form.student_name.data,
                subject=form.subject.data,
                score=form.score.data,
                date=form.date.data
            )
            db.session.add(new_grade)
            db.session.commit()
            flash('Оценка успешно добавлена!', 'success')
            return redirect(url_for('add_grade'))
        
        return render_template('add_grade.html', form=form)
    
✅ Чек-поинт: Коммит feat: add wtf form for grade entry with csrf and validation. Протестируй отправку пустой формы и формы с баллом "150" (должна появиться ошибка).

⏱️ Час 4: Аутентификация и сессии (Flask-Login)
🧠 Концепции для понимания
1. Хеширование паролей: Мы никогда не храним пароли в открытом виде. Хеширование — это одностороннее преобразование: пароль "12345" превращается в набор символов вроде $2b$12$.... Его нельзя "расшифровать" обратно, можно только сравнить хеш введенного пароля с хешем в базе.
2. Сессии и Куки: Как сервер "помнит", что ты вошла в систему? При успешном логине сервер создает зашифрованный ID сессии и отправляет его браузеру в виде cookie. Браузер автоматически прикрепляет эту cookie к каждому следующему запросу, и сервер понимает: "Ага, это тот же самый пользователь".
💻 Практика
1. Установи библиотеку для логина:
    ```bash
    pip install flask-login
2. Настрой app.py:
    ```python
    from flask_login import LoginManager

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login' # Имя роута, куда кидать неавторизованных
3. Добавь модель User в db_models.py:
    ```python
    from flask_login import UserMixin
    from werkzeug.security import generate_password_hash, check_password_hash

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False)
        password_hash = db.Column(db.String(256), nullable=False)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)
4. Реализуй user_loader в app.py (обязательно для Flask-Login, чтобы загружать пользователя по ID из сессии):
    ```python
    from db_models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
5. Создай простые роуты /register и /login в app.py (аналогично add_grade, используй form.validate_on_submit(), user.set_password(), db.session.commit() и функцию login_user(user) из flask_login).
6. Защити роут добавления оценки декоратором:
    ```python
    from flask_login import login_required, current_user

    @app.route('/add_grade', methods=['GET', 'POST'])
    @login_required
    def add_grade():
        # ... логика остается той же
        # В шаблон теперь можно передать current_user.username
    
✅ Чек-поинт: Коммит feat: implement user registration, login and protected routes.

🛡️ Финальный чек-лист перед Pull Request
Перед тем как сделать git push, обязательно выполни:
* black . (форматирование кода)
* ruff check . --fix (поиск и исправление ошибок линтера)
* pytest -v (убедиться, что старые тесты не сломались; можно добавить простой тест на создание объекта User и проверку check_password)
* Проверить через git status, что .env и *.db не попали в коммит.
* Сделать коммит по правилам: git commit -m "feat: complete flask auth and db setup"
* Создать Pull Request в основную ветку и запросить ревью.

💡 Вопросы для рефлексии (обсуди с наставником)
1. Что произойдет, если я случайно удалю файл journal.db? Потеряются ли мои данные навсегда? Как это связано с концепцией "stateless"?
2. Почему мы используем form.validate_on_submit() вместо простой проверки if request.method == 'POST'?
3. Как Flask-Login понимает, что пользователь уже вошел в систему, если HTTP-протокол сам по себе не имеет памяти?
