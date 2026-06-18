from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo

class GradeForm(FlaskForm):
    student_name = StringField('Имя ученика', validators=[DataRequired()])
    subject = StringField('Предмет', validators=[DataRequired()])
    score = IntegerField('Балл', validators=[DataRequired(), NumberRange(min=1, max=5)])
    work_type = StringField('Тип работы', validators=[DataRequired()])
    comment = StringField('Комментарий', validators=[DataRequired()])
    date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Сохранить оценку')

class RegisterForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[DataRequired(), Length(min=3, max=50)]
    )
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Повторите пароль',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Пароль',
        validators=[DataRequired()]
    )
    submit = SubmitField('Войти')