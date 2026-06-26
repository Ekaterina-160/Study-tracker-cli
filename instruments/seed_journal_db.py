from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "instance" / "journal.db"
RANDOM_SEED = 20252026

STUDENTS = [
    "Артём Пельмешкин",
    "Мария Булочкина",
    "Илья Огурцов",
    "София Кнопкина",
    "Даниил Бубликов",
    "Анна Карандашкина",
    "Максим Варежкин",
    "Полина Компоткина",
    "Егор Сырников",
    "Виктория Пятёрочкина",
    "Кирилл Шапочкин",
    "Алиса Пирожкова",
    "Никита Лапшин",
    "Дарья Зефирова",
    "Тимофей Чайников",
    "Елизавета Морковкина",
    "Матвей Кексиков",
    "Варвара Пуговкина",
    "Роман Борщев",
    "Ксения Вафелькина",
    "Глеб Самоваров",
    "Милана Ромашкина",
    "Степан Носочкин",
    "Арина Бараночкина",
    "Фёдор Капустин",
    "Ульяна Смешинкина",
    "Павел Карандашов",
    "Вероника Плюшкина",
    "Ярослав Сапожков",
    "Таисия Конфеткина",
]

SUBJECTS = {
    "Математика": ["Дроби", "Уравнения", "Проценты", "Геометрия"],
    "Русский язык": ["Орфография", "Пунктуация", "Причастия", "Синтаксис"],
    "Литература": ["Стихотворения", "Повесть", "Характеристика героя", "Сочинение"],
    "История": ["Древняя Русь", "Петровские реформы", "XIX век", "Великая Отечественная война"],
    "Биология": ["Клетка", "Растения", "Животные", "Экосистемы"],
    "География": ["Климат", "Материки", "Россия", "Карты"],
    "Физика": ["Сила", "Давление", "Электричество", "Оптика"],
    "Информатика": ["Алгоритмы", "Таблицы", "Python", "Базы данных"],
    "Английский язык": ["Vocabulary", "Grammar", "Reading", "Speaking"],
    "Обществознание": ["Семья", "Экономика", "Право", "Государство"],
}

WORK_TYPES = ["Домашняя работа", "Контрольная работа", "Самостоятельная работа", "Проект", "Устный ответ"]
GRADE_COMMENTS = [
    "Уверенно справился с заданием",
    "Есть прогресс, нужно закрепить тему",
    "Хорошая работа на уроке",
    "Ошибки в деталях, но тема понятна",
    "Отличный результат",
    "Стоит повторить материал",
]
SESSION_NOTES = [
    "Повторение перед уроком",
    "Разбор ошибок после контрольной",
    "Подготовка домашнего задания",
    "Тренировка сложной темы",
    "Работа с дополнительными заданиями",
    "Короткая самостоятельная практика",
]


def iter_school_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def weighted_score(rng: random.Random, student_bias: float, subject_bias: float) -> int:
    value = rng.gauss(4.0 + student_bias + subject_bias, 0.75)
    if value < 2.7:
        return 2
    if value < 3.55:
        return 3
    if value < 4.45:
        return 4
    return 5


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS grade_record (
            id INTEGER NOT NULL PRIMARY KEY,
            student_name VARCHAR(100) NOT NULL,
            subject VARCHAR(50) NOT NULL,
            score INTEGER NOT NULL,
            date DATE NOT NULL,
            work_type VARCHAR(50) NOT NULL,
            comment TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS study_session (
            id INTEGER NOT NULL PRIMARY KEY,
            student_name VARCHAR(100) NOT NULL,
            subject VARCHAR(50) NOT NULL,
            topic VARCHAR(100),
            duration_min INTEGER NOT NULL,
            date DATE,
            notes TEXT
        )
        """
    )


def build_grade_records(rng: random.Random, school_days: list[date]) -> list[tuple[str, str, int, str, str, str]]:
    records: list[tuple[str, str, int, str, str, str]] = []
    subject_biases = {subject: rng.uniform(-0.25, 0.25) for subject in SUBJECTS}

    for student in STUDENTS:
        student_bias = rng.uniform(-0.45, 0.45)
        for subject in SUBJECTS:
            for grade_date in rng.sample(school_days, k=10):
                records.append(
                    (
                        student,
                        subject,
                        weighted_score(rng, student_bias, subject_biases[subject]),
                        grade_date.isoformat(),
                        rng.choice(WORK_TYPES),
                        rng.choice(GRADE_COMMENTS),
                    )
                )

    rng.shuffle(records)
    return records


def build_study_sessions(rng: random.Random, school_days: list[date]) -> list[tuple[str, str, str, int, str, str]]:
    sessions: list[tuple[str, str, str, int, str, str]] = []

    for student in STUDENTS:
        for session_date in rng.sample(school_days, k=18):
            subject = rng.choice(list(SUBJECTS))
            topic = rng.choice(SUBJECTS[subject])
            sessions.append(
                (
                    student,
                    subject,
                    topic,
                    rng.choice([25, 30, 35, 40, 45, 60, 75, 90]),
                    session_date.isoformat(),
                    rng.choice(SESSION_NOTES),
                )
            )

    rng.shuffle(sessions)
    return sessions


def main() -> None:
    if not DB_PATH.parent.exists():
        raise SystemExit(f"Папка БД не найдена: {DB_PATH.parent}")

    rng = random.Random(RANDOM_SEED)
    school_days = iter_school_days(date(2025, 9, 1), date(2026, 5, 31))
    grade_records = build_grade_records(rng, school_days)
    study_sessions = build_study_sessions(rng, school_days)

    with sqlite3.connect(DB_PATH) as conn:
        ensure_tables(conn)
        conn.executemany(
            """
            INSERT INTO grade_record (student_name, subject, score, date, work_type, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            grade_records,
        )
        conn.executemany(
            """
            INSERT INTO study_session (student_name, subject, topic, duration_min, date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            study_sessions,
        )
        conn.commit()

    print(f"Добавлено оценок: {len(grade_records)}")
    print(f"Добавлено учебных сессий: {len(study_sessions)}")
    print(f"База данных: {DB_PATH}")


if __name__ == "__main__":
    main()
