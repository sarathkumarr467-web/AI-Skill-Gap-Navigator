from datetime import datetime
import json
from app.extensions import db

class UserSkillEvidence(db.Model):
    __tablename__ = "user_skill_evidences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    claimed_proficiency = db.Column(db.Integer, default=0) # 0-100
    demonstrated_proficiency = db.Column(db.Integer, default=0) # 0-100
    evidence_source = db.Column(db.String(80), default="Self-Reported") # Assessment, Coding Challenge, Resume, Project, Self-Reported
    verification_status = db.Column(db.String(60), default="Unverified") # Unverified, Self-Reported, Assessment-Verified, Challenge-Verified, Portfolio-Verified
    confidence_score = db.Column(db.Float, default=0.2) # 0.0 - 1.0
    notes = db.Column(db.String(255), default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "skill_id": self.skill_id,
            "skill_name": self.skill.name if self.skill else "",
            "category": self.skill.category if self.skill else "",
            "domain": self.skill.domain if self.skill else "",
            "claimed_proficiency": self.claimed_proficiency,
            "demonstrated_proficiency": self.demonstrated_proficiency,
            "evidence_source": self.evidence_source,
            "verification_status": self.verification_status,
            "confidence_score": round(self.confidence_score, 2),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M")
        }

class PortfolioEvidence(db.Model):
    __tablename__ = "portfolio_evidences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_title = db.Column(db.String(150), nullable=False)
    github_url = db.Column(db.String(255), default="")
    live_url = db.Column(db.String(255), default="")
    description = db.Column(db.Text, nullable=False)
    extracted_tech_json = db.Column(db.Text, default="[]")
    completeness_score = db.Column(db.Integer, default=50) # 0-100
    documentation_rating = db.Column(db.String(30), default="Moderate") # Strong, Moderate, Minimal
    missing_categories_json = db.Column(db.Text, default="[]")
    suggestions_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def extracted_tech(self):
        try:
            return json.loads(self.extracted_tech_json) if self.extracted_tech_json else []
        except Exception:
            return []

    @property
    def missing_categories(self):
        try:
            return json.loads(self.missing_categories_json) if self.missing_categories_json else []
        except Exception:
            return []

    @property
    def suggestions(self):
        try:
            return json.loads(self.suggestions_json) if self.suggestions_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "project_title": self.project_title,
            "github_url": self.github_url,
            "live_url": self.live_url,
            "description": self.description,
            "extracted_tech": self.extracted_tech,
            "completeness_score": self.completeness_score,
            "documentation_rating": self.documentation_rating,
            "missing_categories": self.missing_categories,
            "suggestions": self.suggestions,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }

class SkillGapReport(db.Model):
    __tablename__ = "skill_gap_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=True)
    role_title = db.Column(db.String(120), nullable=False)
    readiness_score = db.Column(db.Float, default=0.0) # 0 - 100
    skill_coverage_pct = db.Column(db.Float, default=0.0)
    critical_gaps_json = db.Column(db.Text, default="[]") # [{skill, current, required, priority, reason}]
    improvement_gaps_json = db.Column(db.Text, default="[]")
    verified_skills_json = db.Column(db.Text, default="[]")
    readiness_breakdown_json = db.Column(db.Text, default="{}") # {coverage: X, proficiency: Y, practical: Z, portfolio: W}
    recommendations_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def critical_gaps(self):
        try:
            return json.loads(self.critical_gaps_json) if self.critical_gaps_json else []
        except Exception:
            return []

    @property
    def improvement_gaps(self):
        try:
            return json.loads(self.improvement_gaps_json) if self.improvement_gaps_json else []
        except Exception:
            return []

    @property
    def verified_skills(self):
        try:
            return json.loads(self.verified_skills_json) if self.verified_skills_json else []
        except Exception:
            return []

    @property
    def readiness_breakdown(self):
        try:
            return json.loads(self.readiness_breakdown_json) if self.readiness_breakdown_json else {}
        except Exception:
            return {}

    @property
    def recommendations(self):
        try:
            return json.loads(self.recommendations_json) if self.recommendations_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "role_title": self.role_title,
            "readiness_score": round(self.readiness_score, 1),
            "skill_coverage_pct": round(self.skill_coverage_pct, 1),
            "critical_gaps": self.critical_gaps,
            "improvement_gaps": self.improvement_gaps,
            "verified_skills": self.verified_skills,
            "readiness_breakdown": self.readiness_breakdown,
            "recommendations": self.recommendations,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }
