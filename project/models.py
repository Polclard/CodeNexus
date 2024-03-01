from enum import Enum
from flask_login import UserMixin
from __init__ import db
from datetime import datetime


class UserRole(Enum):
    ADMIN = 'admin'
    USER = 'user'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    title = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(100000), unique=False, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    code = db.Column(db.String(1000000000), unique=False, nullable=False)
    number_of_attempts = db.Column(db.Integer, nullable=False)
    test_cases = db.Column(db.JSON, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    programming_language = db.Column(db.String(100), unique=False, nullable=False)
    visible = db.Column(db.Boolean, default=False, nullable=False)
    
class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    finish_date = db.Column(db.DateTime)
    submitted = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    number_of_passed_tests = db.Column(db.Integer, default=0)
    grade = db.Column(db.Integer, default=0)
    review = db.Column(db.Boolean, default=True)
    user = db.relationship('User', backref=db.backref('attempts', lazy=True))
    exercise = db.relationship('Exercise', backref=db.backref('attempts', lazy=True))

    test_cases = db.Column(db.String(100000000))
    