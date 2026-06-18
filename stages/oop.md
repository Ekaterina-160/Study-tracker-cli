# 🎯 Занятие 1: Консольный журнал оценок и подготовки
**⏱️ Длительность:** 4 часа  
**📦 Этап:** 1 (CLI + ООП)  
**🎓 Уровень:** Начинающий (после циклов, условий, основ ООП)  
**💻 ОС:** Windows  

---

## 📋 Цели занятия
- [ ] Настроить рабочее окружение (Python, Git, виртуальное окружение)
- [ ] Создать две независимые сущности: `GradeRecord` (оценка) и `StudySession` (подготовка)
- [ ] Реализовать консольное меню с добавлением данных и просмотром статистики
- [ ] Настроить сохранение/загрузку из JSON-файлов
- [ ] Добавить базовые тесты, линтинг и документацию
- [ ] Опубликовать проект на GitHub и вести DEVLOG

---

## ⏰ План занятия (тайминг)

| Блок | Время | Что делаем |
|------|-------|------------|
| **0. Подготовка** | 15 мин | Терминал, Git, venv, `.gitignore` |
| **1. Модель данных** | 60 мин | `models.py` — сущности, репозитории, аналитика |
| **2. Консольное меню** | 60 мин | `main.py` — интерактивный CLI |
| **3. Качество кода** | 45 мин | Тесты, `black`/`ruff`, `README.md` |
| **4. Финализация** | 30 мин | Пуш на GitHub, DEVLOG, проверка |

---

## 🛠️ Блок 0: Подготовка (15 минут)

### 1. Открыть PowerShell
`Win + X` → `Windows PowerShell`

### 2. Создать папку и перейти в неё
```powershell
mkdir study-journal-cli
cd study-journal-cli
```

### 3. Инициализировать Git
```powershell
git init
git branch -M main
```

### 4. Создать виртуальное окружение и активировать
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
✅ В строке должен появиться префикс `(.venv)`.

### 5. Создать `.gitignore`
```gitignore
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Данные
grades.json
sessions.json
data.json
*.sqlite

# Окружение
.env
```

### 6. Первый коммит
```powershell
git add .gitignore
git commit -m "init: project setup + gitignore"
```

---

## 💻 Блок 1: Модель данных (60 минут)

Создайте файл `models.py` и вставьте код:

```python
# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json
import os


# ========== Сущность 1: Оценка ==========
@dataclass
class GradeRecord:
    """Факт получения оценки"""
    id: int
    student_name: str
    subject: str
    grade: float
    recorded_at: datetime
    assessment_type: str
    comment: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "student_name": self.student_name,
            "subject": self.subject,
            "grade": self.grade,
            "recorded_at": self.recorded_at.isoformat(),
            "assessment_type": self.assessment_type,
            "comment": self.comment
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GradeRecord":
        data["recorded_at"] = datetime.fromisoformat(data["recorded_at"])
        return cls(**data)


# ========== Сущность 2: Сессия подготовки ==========
@dataclass
class StudySession:
    """Факт подготовки к предмету"""
    id: int
    student_name: str
    subject: str
    topic: str
    duration_min: int
    date: datetime
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "student_name": self.student_name,
            "subject": self.subject,
            "topic": self.topic,
            "duration_min": self.duration_min,
            "date": self.date.isoformat(),
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StudySession":
        data["date"] = datetime.fromisoformat(data["date"])
        return cls(**data)


# ========== Репозиторий оценок ==========
class GradeRepository:
    def __init__(self, filepath: str = "grades.json"):
        self.filepath = filepath
        self.records: List[GradeRecord] = []
        self._next_id: int = 1
        self._load()

    def add(self, student_name: str, subject: str, grade: float, 
            assessment_type: str, comment: str = "") -> GradeRecord:
        record = GradeRecord(
            id=self._next_id, student_name=student_name, subject=subject,
            grade=grade, recorded_at=datetime.now(),
            assessment_type=assessment_type, comment=comment
        )
        self.records.append(record)
        self._next_id += 1
        self._save()
        return record

    def get_all(self) -> List[GradeRecord]:
        return self.records.copy()

    def get_by_subject(self, subject: str) -> List[GradeRecord]:
        return [r for r in self.records if r.subject.lower() == subject.lower()]

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in self.records], f, indent=2, ensure_ascii=False)

    def _load(self):
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.records = [GradeRecord.from_dict(d) for d in raw]
        if self.records:
            self._next_id = max(r.id for r in self.records) + 1


# ========== Репозиторий сессий ==========
class SessionRepository:
    def __init__(self, filepath: str = "sessions.json"):
        self.filepath = filepath
        self.sessions: List[StudySession] = []
        self._next_id: int = 1
        self._load()

    def add(self, student_name: str, subject: str, topic: str, 
            duration_min: int, notes: str = "") -> StudySession:
        session = StudySession(
            id=self._next_id, student_name=student_name, subject=subject,
            topic=topic, duration_min=duration_min, date=datetime.now(), notes=notes
        )
        self.sessions.append(session)
        self._next_id += 1
        self._save()
        return session

    def get_all(self) -> List[StudySession]:
        return self.sessions.copy()

    def get_by_subject(self, subject: str) -> List[StudySession]:
        return [s for s in self.sessions if s.subject.lower() == subject.lower()]

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.sessions], f, indent=2, ensure_ascii=False)

    def _load(self):
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.sessions = [StudySession.from_dict(d) for d in raw]
        if self.sessions:
            self._next_id = max(s.id for s in self.sessions) + 1


# ========== Аналитика ==========
class GradeAnalytics:
    @staticmethod
    def average_grade(records: List[GradeRecord]) -> Optional[float]:
        if not records: return None
        return round(sum(r.grade for r in records) / len(records), 2)

    @staticmethod
    def by_subject(records: List[GradeRecord]) -> dict:
        groups = {}
        for r in records:
            groups.setdefault(r.subject, []).append(r.grade)
        return {subj: round(sum(g)/len(g), 2) for subj, g in groups.items()}


class SessionAnalytics:
    @staticmethod
    def total_hours(sessions: List[StudySession]) -> float:
        return round(sum(s.duration_min for s in sessions) / 60, 2)

    @staticmethod
    def by_subject(sessions: List[StudySession]) -> dict:
        groups = {}
        for s in sessions:
            groups.setdefault(s.subject, []).append(s.duration_min)
        return {subj: round(sum(m)/60, 2) for subj, m in groups.items()}
```

### Проверка
```powershell
python -c "from models import GradeRecord, StudySession; print('✅ OK')"
git add models.py
git commit -m "feat: add independent data models"
```

---

## 🖥️ Блок 2: Консольное меню (60 минут)

Создайте `main.py`:

```python
# main.py
from models import GradeRepository, SessionRepository, GradeAnalytics, SessionAnalytics

def print_menu():
    print("\n📚 Study Journal CLI")
    print("=" * 30)
    print("1. Добавить оценку")
    print("2. Добавить сессию подготовки")
    print("3. Статистика по оценкам")
    print("4. Статистика по подготовке")
    print("5. Выход")
    print("=" * 30)

def add_grade(repo: GradeRepository):
    print("\n➕ Новая оценка")
    student = input("Имя ученика: ").strip()
    subject = input("Предмет: ").strip()
    grade = float(input("Оценка (2-5): "))
    atype = input("Тип (test/quiz/exam/homework): ").strip()
    comment = input("Комментарий: ").strip()
    repo.add(student, subject, grade, atype, comment)
    print("✅ Сохранено!")

def add_session(repo: SessionRepository):
    print("\n📖 Новая сессия")
    student = input("Имя ученика: ").strip()
    subject = input("Предмет: ").strip()
    topic = input("Тема: ").strip()
    duration = int(input("Минуты: "))
    notes = input("Заметки: ").strip()
    repo.add(student, subject, topic, duration, notes)
    print("✅ Сохранено!")

def show_grade_stats(repo: GradeRepository):
    records = repo.get_all()
    if not records: print("\n📭 Нет оценок"); return
    print(f"\n📊 Всего: {len(records)} | Средний балл: {GradeAnalytics.average_grade(records)}")
    for subj, avg in sorted(GradeAnalytics.by_subject(records).items()):
        print(f"  • {subj}: {avg}")

def show_session_stats(repo: SessionRepository):
    sessions = repo.get_all()
    if not sessions: print("\n📭 Нет записей"); return
    print(f"\n📊 Всего: {len(sessions)} | Часов: {SessionAnalytics.total_hours(sessions)}")
    for subj, hrs in sorted(SessionAnalytics.by_subject(sessions).items()):
        print(f"  • {subj}: {hrs} ч")

def main():
    grade_repo = GradeRepository()
    session_repo = SessionRepository()
    print("👋 Добро пожаловать!")
    while True:
        print_menu()
        choice = input("\nВыбор (1-5): ").strip()
        if choice == "1": add_grade(grade_repo)
        elif choice == "2": add_session(session_repo)
        elif choice == "3": show_grade_stats(grade_repo)
        elif choice == "4": show_session_stats(session_repo)
        elif choice == "5": print("👋 До связи!"); break
        else: print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
```

### Проверка
```powershell
python main.py
# Добавьте 2 оценки и 2 сессии, проверьте пункты 3 и 4, выйдите (5)
# Запустите снова — данные должны остаться
git add main.py
git commit -m "feat: add interactive CLI menu"
```

---

## 🧪 Блок 3: Тесты, линтинг, документация (45 минут)

### 1. Установка инструментов
```powershell
pip install black ruff pytest
pip freeze > requirements.txt
```

### 2. Настройка `pyproject.toml`
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "W"]

[tool.pytest.ini_options]
python_files = "test_*.py"
testpaths = ["."]
```

### 3. Тесты `test_models.py`
```python
from models import GradeRecord, StudySession, GradeAnalytics, SessionAnalytics
from datetime import datetime

def test_avg_grade():
    recs = [
        GradeRecord(1, "Аня", "Матем", 5.0, datetime.now(), "test"),
        GradeRecord(2, "Аня", "Матем", 4.0, datetime.now(), "quiz")
    ]
    assert GradeAnalytics.average_grade(recs) == 4.5

def test_total_hours():
    sess = [
        StudySession(1, "Аня", "Матем", "Алгебра", 45, datetime.now()),
        StudySession(2, "Аня", "Матем", "Геом", 60, datetime.now())
    ]
    assert SessionAnalytics.total_hours(sess) == 1.75

def test_by_subject():
    recs = [GradeRecord(1, "Аня", "Матем", 5.0, datetime.now(), "test")]
    assert GradeAnalytics.by_subject(recs)["Матем"] == 5.0
```

### 4. Проверка качества
```powershell
pytest -v
black .
ruff check . --fix
```

### 5. `README.md`
```markdown
# 📚 Study Journal CLI
Консольный журнал оценок и времени подготовки.

## 🚀 Запуск
\`\`\`powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
\`\`\`

## 📦 Структура
- `models.py` — данные и логика
- `main.py` — интерфейс
- `grades.json` / `sessions.json` — хранилища

## 🧪 Тесты
\`\`\`powershell
pytest
\`\`\`
```

### Коммит
```powershell
git add requirements.txt test_models.py pyproject.toml README.md
git commit -m "chore: add tests, linting, docs"
```

---

## 🚀 Блок 4: Финализация и GitHub (30 минут)

### 1. Создать репозиторий на GitHub
1. `github.com` → `+` → `New repository`
2. Имя: `study-journal-cli`, Public, без README
3. Создать

### 2. Пуш
```powershell
git remote add origin https://github.com/ВАШ_НИК/study-journal-cli.git
git push -u origin main
```

### 3. DEVLOG.md (рефлексия)
```markdown
# 📘 DEVLOG
**📅 Дата:** ____ | **⏱️ 4 ч** | **🎯 Этап 1**

### ✅ Сделано
- Окружение, Git, venv
- Две независимые модели + репозитории
- CLI с сохранением в JSON
- Тесты, линтер, README

### 💡 Инсайты
- `@dataclass` убирает бойлерплейт
- Разделение сущностей упрощает тестирование
- Git даёт уверенность при экспериментах

### ❓ Вопросы
- Как связать подготовку с оценками? (Этап 3)
- Как добавить поиск по ученику? (следующая ветка)

### 🎯 План на завтра
- Ветка `feature/search`
- Поиск по `student_name`
- Изучить Flask-базу
```

### Финальный коммит
```powershell
git add DEVLOG.md
git commit -m "docs: add devlog lesson 1"
git push
```

---

## ✅ Итоговый чек-лист
- [ ] `python main.py` → меню работает, данные сохраняются
- [ ] `pytest -v` → 3/3 PASSED
- [ ] `black .` / `ruff check .` → чисто
- [ ] На GitHub нет `.venv/`, `__pycache__/`, JSON-файлов
- [ ] `README.md` и `DEVLOG.md` заполнены
- [ ] `git log` показывает чистую историю коммитов

---

## 🆘 Частые проблемы (Windows)
| Ошибка | Решение |
|--------|---------|
| `Activate.ps1` заблокирован | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `pytest: not found` | Проверьте префикс `(.venv)` в терминале |
| `JSONDecodeError` | Удалите `grades.json`/`sessions.json` — создадутся заново |
| Git просит пароль | Используйте [Personal Access Token](https://github.com/settings/tokens) |

---
🎉 **Занятие завершено. Переходите к ветке `feature/search` или начинайте изучение Flask.**
