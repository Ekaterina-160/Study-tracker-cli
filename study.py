import json
import models


grade_analytics = models.GradeAnalytics()
grade_repository = models.GradeRepository()
while True:
    print('Выберите действие:')
    print('1 - добавить запись об оценке')
    print('2 - прочитать все записи об оценках по предмету')
    print('3 - прочитать все записи')
    print('4 - посчитать общий средний балл')
    print('5 - посчитать средний балл по предмету')
    print('6 - посчитать средний балл ученика по всем предметам')
    print('7 - прочитать записи об ученике')
    print('0 - выйти')
    user_answer = int(input())
    if user_answer == 1:
        class_number = input('Введите класс:')
        student_name = input('ФИО ученика:')
        subject = input('Предмет:')
        grade = int(input('Оценка:'))
        assessment_type = input('Тип оценки:')
        comment = input('Комментарий:')
        grade_repository.add(class_number, student_name, subject, grade, assessment_type, comment)
        print(grade_repository.get_all())
    elif user_answer == 2:
        subject = input('Введите предмет:')
        print(grade_repository.get_by_subject(subject))
    
    elif user_answer == 3:
        print(grade_repository.get_all())
    elif user_answer == 4:
        all = grade_repository.get_all()
        print(grade_analytics.average_grade(all))
    elif user_answer == 5:
        all = grade_repository.get_all()
        print(grade_analytics.by_subject(all))
    elif user_answer == 6:
        all = grade_repository.get_all()
        student_n = input('Введите ФИО ')
        print(grade_analytics.average_student(all, student_n))
    elif user_answer == 7:
        student = input('Введите ФИО:')
        print(grade_repository.get_by_student(student))
    if user_answer == 0:
        break
    