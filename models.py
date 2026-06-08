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
    class_number: int
    student_name: str
    subject: str
    grade: float
    recorded_at: datetime
    assessment_type: str
    comment: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "class_number": self.class_number,
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
        data["grade"] = float(data["grade"])
        data["class_number"] = int(data["class_number"])
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

    def add(self, class_number: int, student_name: str, subject: str, grade: float,
            assessment_type: str, comment: str = "") -> GradeRecord:
        record = GradeRecord(
            id=self._next_id, class_number=class_number, student_name=student_name, subject=subject,
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
    
    def get_by_student(self, student: str) -> List[GradeRecord]:
        return [s for s in self.records if s.student_name.lower() == student.lower()]

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
    
    @staticmethod
    def average_student(records: List[GradeRecord], student_n: str) -> Optional[float]:
        if not records:
            return None
        student = [r for r in records if student_n.lower() == r.student_name.lower()]
        if not student:
            return None
        return round(sum(r.grade for r in student) / len(student), 2)

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