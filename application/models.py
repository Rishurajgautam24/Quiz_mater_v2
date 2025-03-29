from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ------- User Management Models -------
class RolesUsers(db.Model):
    """Junction Table For User-Role Relationships"""
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user_table.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role_table.id'))

class User(db.Model, UserMixin):
    """User Model With Authentication Features"""
    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='roles_users',
                         backref=db.backref('users', lazy='dynamic'))
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role_table'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

# ------- Course Management Models -------
class Subject(db.Model):
    """Subject Model With Chapter Relationships"""
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

class Chapter(db.Model):
    """Chapter Model With Quiz Relationships"""
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

# ------- Quiz Management Models -------
class Quiz(db.Model):
    """Quiz Model With Questions And Attempts"""
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # duration in minutes
    start_time = db.Column(db.DateTime)  # New field for scheduled start
    end_time = db.Column(db.DateTime)    # New field for scheduled end
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

    @property
    def is_active(self):
        """Check if quiz is currently active"""
        now = datetime.utcnow()
        return (
            self.start_time and 
            self.end_time and 
            self.start_time <= now <= self.end_time
        )

    @property
    def status(self):
        """Get quiz status"""
        now = datetime.utcnow()
        if not self.start_time or not self.end_time:
            return "draft"
        if now < self.start_time:
            return "scheduled"
        if now > self.end_time:
            return "expired"
        return "active"

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # Store options as JSON array
    correct_answer = db.Column(db.Integer, nullable=False)  # Index of correct option
    marks = db.Column(db.Integer, default=1)

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_table.id'), nullable=False)
    score = db.Column(db.Float, nullable=False, default=0.0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add this field
    completed_at = db.Column(db.DateTime)
    answers = db.Column(db.JSON)  # Store user answers as JSON
    response_sheet = db.Column(db.JSON)  # Store detailed response data

    @property
    def duration(self):
        """Calculate duration in minutes"""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds() / 60, 1)
        return None

