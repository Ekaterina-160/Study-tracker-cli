from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class GradeForm(FlaskForm):
    student_name = StringField('Имя ученика', validators=[DataRequired()])
    subject = StringField('Предмет', validators=[DataRequired()])
    score = IntegerField('Балл', validators=[DataRequired(), NumberRange(min=1, max=5)])
    work_type = StringField('Тип работы', validators=[DataRequired()])
    comment = StringField('Комментарий', validators=[DataRequired()])
    date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Сохранить оценку')