from datetime import datetime
from extensions import db

class GradeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    work_type = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.Text)

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(100))
    duration_min = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.Text)
