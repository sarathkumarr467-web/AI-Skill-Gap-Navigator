from datetime import datetime
import json
from app.extensions import db

class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False)
    domain = db.Column(db.String(80), nullable=False) # Core, Data Science, AI/ML, DevOps, Web
    importance = db.Column(db.String(30), default="High") # Critical, High, Medium, Low
    description = db.Column(db.Text, default="")
    prerequisites_json = db.Column(db.Text, default="[]") # JSON list of prerequisite skill names
    estimated_learning_hours = db.Column(db.Integer, default=20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    role_requirements = db.relationship("RoleRequirement", backref="skill", cascade="all, delete-orphan", lazy="dynamic")
    user_evidences = db.relationship("UserSkillEvidence", backref="skill", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def prerequisites(self):
        try:
            return json.loads(self.prerequisites_json) if self.prerequisites_json else []
        except Exception:
            return []

    @prerequisites.setter
    def prerequisites(self, val):
        self.prerequisites_json = json.dumps(val)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "category": self.category,
            "domain": self.domain,
            "importance": self.importance,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "estimated_learning_hours": self.estimated_learning_hours
        }

class SkillDependency(db.Model):
    __tablename__ = "skill_dependencies"

    id = db.Column(db.Integer, primary_key=True)
    source_skill = db.Column(db.String(100), nullable=False, index=True)
    target_skill = db.Column(db.String(100), nullable=False, index=True) # target requires source
    relation_type = db.Column(db.String(50), default="prerequisite") # prerequisite, corequisite, recommended
    reason = db.Column(db.String(255), default="")

    def to_dict(self):
        return {
            "id": self.id,
            "source_skill": self.source_skill,
            "target_skill": self.target_skill,
            "relation_type": self.relation_type,
            "reason": self.reason
        }
