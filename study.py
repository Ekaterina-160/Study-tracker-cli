import json
a = {'entries':[]}
informatoin = {}
informatoin['school_number'] = input('Номер школы:')
informatoin['class'] = input('Класс:')
informatoin['subject'] = input('Предмет:')
informatoin['student_last_name'] = input('Фамилия ученика:')
informatoin['student_first_name'] = input('Имя ученика:')
informatoin['data_assesment'] = input('Дата оценки:')
informatoin['assesment'] = input('Оценка:')
a['entries'].append(informatoin)
with open("a.json", "w", encoding="utf-8") as file:
    json.dump(a, file)
with open("a.json", "r", encoding="utf-8") as file:
    loaded_a = json.load(file)
print(loaded_a)