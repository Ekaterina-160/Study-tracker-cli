import models


def read_int(prompt: str) -> int:
    while True:
        value = input(prompt).strip()
        try:
            return int(value)
        except ValueError:
            print("Ошибка: введите целое число.")


grade_analytics = models.GradeAnalytics()
grade_repository = models.GradeRepository()

while True:
    print("Выберите действие:")
    print("1 - добавить запись об оценке")
    print("2 - прочитать все записи об оценках по предмету")
    print("3 - прочитать все записи")
    print("4 - посчитать общий средний балл")
    print("5 - посчитать средний балл по предмету")
    print("6 - посчитать средний балл ученика по всем предметам")
    print("7 - прочитать записи об ученике")
    print("0 - выйти")

    try:
        user_answer = int(input().strip())
    except ValueError:
        print("Ошибка: введите номер пункта меню (0–7).")
        continue

    if user_answer == 1:
        class_number = read_int("Введите класс: ")
        student_name = input("ФИО ученика: ")
        subject = input("Предмет: ")
        grade = read_int("Оценка: ")
        assessment_type = input("Тип оценки: ")
        comment = input("Комментарий: ")
        grade_repository.add(class_number, student_name, subject, grade, assessment_type, comment)
        print(grade_repository.get_all())
    elif user_answer == 2:
        subject = input("Введите предмет: ")
        print(grade_repository.get_by_subject(subject))
    elif user_answer == 3:
        print(grade_repository.get_all())
    elif user_answer == 4:
        records = grade_repository.get_all()
        result = grade_analytics.average_grade(records)
        if result is None:
            print("Нет записей для расчёта.")
        else:
            print(result)
    elif user_answer == 5:
        records = grade_repository.get_all()
        print(grade_analytics.by_subject(records))
    elif user_answer == 6:
        records = grade_repository.get_all()
        student_n = input("Введите ФИО: ")
        result = grade_analytics.average_student(records, student_n)
        if result is None:
            print("Ученик не найден или нет записей.")
        else:
            print(result)
    elif user_answer == 7:
        student = input("Введите ФИО: ")
        print(grade_repository.get_by_student(student))
    elif user_answer == 0:
        break
    else:
        print("Неизвестный пункт меню. Выберите число от 0 до 7.")
