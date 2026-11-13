from flask import Blueprint, render_template, jsonify
from app.models.user import User, Notification
from app.models.career import CareerRole
from app.models.evidence import UserSkillEvidence, SkillGapReport
from app.models.roadmap import LearningRoadmap
from app.models.assessment import AssessmentAttempt, CodingSubmission
from app.models.progress import ProgressSnapshot
from app.utils.auth import login_required, get_current_user
from app.services.readiness_service import JobReadinessService
from app.services.gap_service import SkillGapService
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()

    # Find or default target career role
    role = CareerRole.query.filter_by(title=user.target_career).first()
    if not role:
        role = CareerRole.query.first()

    # User evidences
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()
    verified_skills = [e for e in evidences if e.demonstrated_proficiency >= 60]

    # Latest gap report or compute on the fly
    latest_report = SkillGapReport.query.filter_by(user_id=user.id).order_by(SkillGapReport.created_at.desc()).first()
    
    # Active roadmap
    roadmap = LearningRoadmap.query.filter_by(user_id=user.id, status="active").first()

    # Recent assessments & coding submissions
    recent_attempts = AssessmentAttempt.query.filter_by(user_id=user.id).order_by(AssessmentAttempt.completed_at.desc()).limit(5).all()
    recent_coding = CodingSubmission.query.filter_by(user_id=user.id).order_by(CodingSubmission.submitted_at.desc()).limit(5).all()

    # Calculate current readiness score
    avg_assessment = sum(a.percentage for a in recent_attempts) / len(recent_attempts) if recent_attempts else 0.0
    passed_coding = sum(1 for c in recent_coding if c.status == "PASSED")
    coding_pct = (passed_coding / len(recent_coding) * 100) if recent_coding else 0.0
    
    coverage_pct = latest_report.skill_coverage_pct if latest_report else 0.0
    crit_missing = len(latest_report.critical_gaps) if latest_report else 3

    readiness_data = JobReadinessService.calculate_readiness(
        coverage_pct=coverage_pct,
        assessment_avg_pct=avg_assessment,
        coding_challenges_passed_pct=coding_pct,
        portfolio_score_pct=65.0 if user.portfolio_items.count() > 0 else 20.0,
        critical_missing_count=crit_missing
    )

    # Notifications
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(5).all()

    # Progress snapshot history for line chart
    snapshots = ProgressSnapshot.query.filter_by(user_id=user.id).order_by(ProgressSnapshot.snapshot_date.asc()).all()

    return render_template(
        "dashboard.html",
        user=user,
        role=role,
        readiness=readiness_data,
        verified_skills=verified_skills,
        report=latest_report,
        roadmap=roadmap,
        recent_attempts=recent_attempts,
        recent_coding=recent_coding,
        notifications=notifications,
        snapshots=snapshots
    )

@dashboard_bp.route("/api/dashboard/stats")
@login_required
def dashboard_stats():
    user = get_current_user()
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()
    
    labels = [e.skill.name for e in evidences if e.skill][:8]
    data = [e.demonstrated_proficiency for e in evidences if e.skill][:8]

    return jsonify({
        "skills_labels": labels if labels else ["Python", "SQL", "ML", "Git", "Docker"],
        "skills_scores": data if data else [0, 0, 0, 0, 0]
    })
