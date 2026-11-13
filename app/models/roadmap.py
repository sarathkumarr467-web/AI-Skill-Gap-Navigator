from datetime import datetime
import json
from app.extensions import db

class LearningRoadmap(db.Model):
    __tablename__ = "learning_roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = db.Column(db.String(120), nullable=False)
    total_weeks = db.Column(db.Integer, default=8)
    weekly_hours = db.Column(db.Integer, default=10)
    current_week = db.Column(db.Integer, default=1)
    status = db.Column(db.String(40), default="active") # active, completed, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    milestones = db.relationship("RoadmapMilestone", backref="roadmap", cascade="all, delete-orphan", lazy="joined", order_by="RoadmapMilestone.week_number")

    def to_dict(self):
        completed_count = sum(1 for m in self.milestones if m.is_completed)
        progress_pct = (completed_count / len(self.milestones) * 100) if self.milestones else 0.0
        return {
            "id": self.id,
            "target_role": self.target_role,
            "total_weeks": self.total_weeks,
            "weekly_hours": self.weekly_hours,
            "current_week": self.current_week,
            "status": self.status,
            "completed_milestones": completed_count,
            "total_milestones": len(self.milestones),
            "progress_pct": round(progress_pct, 1),
            "milestones": [m.to_dict() for m in self.milestones]
        }

class RoadmapMilestone(db.Model):
    __tablename__ = "roadmap_milestones"

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("learning_roadmaps.id", ondelete="CASCADE"), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    objectives_json = db.Column(db.Text, default="[]")
    practice_tasks_json = db.Column(db.Text, default="[]")
    resources_json = db.Column(db.Text, default="[]")
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    @property
    def objectives(self):
        try:
            return json.loads(self.objectives_json) if self.objectives_json else []
        except Exception:
            return []

    @property
    def practice_tasks(self):
        try:
            return json.loads(self.practice_tasks_json) if self.practice_tasks_json else []
        except Exception:
            return []

    @property
    def resources(self):
        try:
            return json.loads(self.resources_json) if self.resources_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "week_number": self.week_number,
            "title": self.title,
            "skill_name": self.skill_name,
            "objectives": self.objectives,
            "practice_tasks": self.practice_tasks,
            "resources": self.resources,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.strftime("%Y-%m-%d") if self.completed_at else None
        }

class LearningResource(db.Model):
    __tablename__ = "learning_resources"

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    resource_type = db.Column(db.String(50), default="Documentation") # Documentation, Tutorial, Course, Book
    level = db.Column(db.String(30), default="Beginner") # Beginner, Intermediate, Advanced
    url = db.Column(db.String(255), nullable=False)
    estimated_hours = db.Column(db.Integer, default=10)
    is_free = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, default="")

    def to_dict(self):
        return {
            "id": self.id,
            "skill_name": self.skill_name,
            "title": self.title,
            "resource_type": self.resource_type,
            "level": self.level,
            "url": self.url,
            "estimated_hours": self.estimated_hours,
            "is_free": self.is_free,
            "description": self.description
        }

class ProjectRecommendation(db.Model):
    __tablename__ = "project_recommendations"

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(30), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(30), default="Intermediate")
    target_gap = db.Column(db.String(100), nullable=False, index=True)
    skills_developed_json = db.Column(db.Text, default="[]")
    tech_stack_json = db.Column(db.Text, default="[]")
    learning_objectives_json = db.Column(db.Text, default="[]")
    deliverables_json = db.Column(db.Text, default="[]")
    validation_checklist_json = db.Column(db.Text, default="[]")
    portfolio_value = db.Column(db.Text, default="")

    @property
    def skills_developed(self):
        try:
            return json.loads(self.skills_developed_json) if self.skills_developed_json else []
        except Exception:
            return []

    @property
    def tech_stack(self):
        try:
            return json.loads(self.tech_stack_json) if self.tech_stack_json else []
        except Exception:
            return []

    @property
    def learning_objectives(self):
        try:
            return json.loads(self.learning_objectives_json) if self.learning_objectives_json else []
        except Exception:
            return []

    @property
    def deliverables(self):
        try:
            return json.loads(self.deliverables_json) if self.deliverables_json else []
        except Exception:
            return []

    @property
    def validation_checklist(self):
        try:
            return json.loads(self.validation_checklist_json) if self.validation_checklist_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "project_code": self.project_code,
            "title": self.title,
            "difficulty": self.difficulty,
            "target_gap": self.target_gap,
            "skills_developed": self.skills_developed,
            "tech_stack": self.tech_stack,
            "learning_objectives": self.learning_objectives,
            "deliverables": self.deliverables,
            "validation_checklist": self.validation_checklist,
            "portfolio_value": self.portfolio_value
        }
