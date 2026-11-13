from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    target_career = db.Column(db.String(100), default="AI Engineer")
    study_hours_per_week = db.Column(db.Integer, default=10)
    current_education = db.Column(db.String(120), default="Undergraduate / Recent Graduate")
    bio = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skill_evidences = db.relationship("UserSkillEvidence", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    assessment_attempts = db.relationship("AssessmentAttempt", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    gap_reports = db.relationship("SkillGapReport", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    roadmaps = db.relationship("LearningRoadmap", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    coding_submissions = db.relationship("CodingSubmission", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    portfolio_items = db.relationship("PortfolioEvidence", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    interview_sessions = db.relationship("MockInterviewSession", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    progress_snapshots = db.relationship("ProgressSnapshot", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "target_career": self.target_career,
            "study_hours_per_week": self.study_hours_per_week,
            "current_education": self.current_education,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="info") # info, success, warning, alert
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "category": self.category,
            "is_read": self.is_read,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }
