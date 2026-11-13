from datetime import datetime
from app.extensions import db

class ProgressSnapshot(db.Model):
    __tablename__ = "progress_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = db.Column(db.String(120), nullable=False)
    readiness_score = db.Column(db.Float, default=0.0)
    verified_skills_count = db.Column(db.Integer, default=0)
    total_gaps_count = db.Column(db.Integer, default=0)
    roadmap_progress_pct = db.Column(db.Float, default=0.0)
    snapshot_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "target_role": self.target_role,
            "readiness_score": round(self.readiness_score, 1),
            "verified_skills_count": self.verified_skills_count,
            "total_gaps_count": self.total_gaps_count,
            "roadmap_progress_pct": round(self.roadmap_progress_pct, 1),
            "snapshot_date": self.snapshot_date.strftime("%Y-%m-%d")
        }
