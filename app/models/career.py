from datetime import datetime
import json
from app.extensions import db

class CareerRole(db.Model):
    __tablename__ = "career_roles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    soc_code = db.Column(db.String(20), nullable=True) # O*NET SOC code
    domain = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default="")
    benchmark_role = db.Column(db.Boolean, default=True)
    avg_salary_range = db.Column(db.String(60), default="$85,000 - $145,000")
    growth_outlook = db.Column(db.String(60), default="Much Faster than Average (+22%)")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requirements = db.relationship("RoleRequirement", backref="career_role", cascade="all, delete-orphan", lazy="joined")
    gap_reports = db.relationship("SkillGapReport", backref="career_role", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "soc_code": self.soc_code,
            "domain": self.domain,
            "description": self.description,
            "benchmark_role": self.benchmark_role,
            "avg_salary_range": self.avg_salary_range,
            "growth_outlook": self.growth_outlook,
            "requirements": [r.to_dict() for r in self.requirements]
        }

class RoleRequirement(db.Model):
    __tablename__ = "role_requirements"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    required_proficiency = db.Column(db.Integer, default=70) # 0-100 scale
    importance_weight = db.Column(db.Float, default=1.0) # 0.5 to 2.0
    is_critical = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "skill_id": self.skill_id,
            "skill_name": self.skill.name if self.skill else "",
            "category": self.skill.category if self.skill else "",
            "required_proficiency": self.required_proficiency,
            "importance_weight": self.importance_weight,
            "is_critical": self.is_critical
        }

class JobPosting(db.Model):
    __tablename__ = "job_postings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(120), default="Tech Corp")
    location = db.Column(db.String(100), default="Remote / Hybrid")
    experience_level = db.Column(db.String(50), default="Entry-Level / Junior")
    raw_description = db.Column(db.Text, nullable=False)
    extracted_skills_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def extracted_skills(self):
        try:
            return json.loads(self.extracted_skills_json) if self.extracted_skills_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "experience_level": self.experience_level,
            "extracted_skills": self.extracted_skills,
            "created_at": self.created_at.strftime("%Y-%m-%d")
        }
