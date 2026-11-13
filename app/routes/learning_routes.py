from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.roadmap import LearningRoadmap, RoadmapMilestone, LearningResource, ProjectRecommendation
from app.models.career import CareerRole
from app.models.evidence import SkillGapReport
from app.services.roadmap_service import RoadmapGeneratorService
from app.utils.auth import login_required, get_current_user

learning_bp = Blueprint("learning", __name__)

@learning_bp.route("/roadmap")
@login_required
def roadmap():
    user = get_current_user()
    active_roadmap = LearningRoadmap.query.filter_by(user_id=user.id, status="active").first()
    
    if not active_roadmap:
        # Check if user has a gap report to generate from
        latest_report = SkillGapReport.query.filter_by(user_id=user.id).order_by(SkillGapReport.created_at.desc()).first()
        gaps = latest_report.critical_gaps + latest_report.improvement_gaps if latest_report else [
            {"skill": "Python"}, {"skill": "SQL"}, {"skill": "Machine Learning Modeling"}
        ]
        
        service = RoadmapGeneratorService()
        active_roadmap = service.generate_roadmap(
            user_id=user.id,
            target_role=user.target_career or "AI Engineer",
            gaps=gaps,
            weekly_hours=user.study_hours_per_week
        )
        flash("Personalized learning roadmap generated based on your target career!", "info")

    return render_template("learning/roadmap.html", roadmap=active_roadmap)

@learning_bp.route("/roadmap/generate", methods=["POST"])
@login_required
def generate_roadmap():
    user = get_current_user()
    weekly_hours = int(request.form.get("weekly_hours", user.study_hours_per_week))
    
    latest_report = SkillGapReport.query.filter_by(user_id=user.id).order_by(SkillGapReport.created_at.desc()).first()
    gaps = latest_report.critical_gaps + latest_report.improvement_gaps if latest_report else [
        {"skill": "Python"}, {"skill": "Scikit-Learn"}, {"skill": "MLOps & Model Deployment"}
    ]

    service = RoadmapGeneratorService()
    new_roadmap = service.generate_roadmap(
        user_id=user.id,
        target_role=user.target_career or "AI Engineer",
        gaps=gaps,
        weekly_hours=weekly_hours
    )
    flash(f"Generated new {new_roadmap.total_weeks}-week roadmap tailored to {weekly_hours} hours/week!", "success")
    return redirect(url_for("learning.roadmap"))

@learning_bp.route("/roadmap/milestone/<int:milestone_id>/toggle", methods=["POST"])
@login_required
def toggle_milestone(milestone_id):
    milestone = RoadmapMilestone.query.get_or_404(milestone_id)
    milestone.is_completed = not milestone.is_completed
    milestone.completed_at = datetime.utcnow() if milestone.is_completed else None
    db.session.commit()
    return redirect(url_for("learning.roadmap"))

@learning_bp.route("/resources")
@login_required
def resources():
    skill_filter = request.args.get("skill", "All")
    level_filter = request.args.get("level", "All")

    query = LearningResource.query
    if skill_filter != "All":
        query = query.filter_by(skill_name=skill_filter)
    if level_filter != "All":
        query = query.filter_by(level=level_filter)

    items = query.all()
    all_skills = sorted(list(set(r.skill_name for r in LearningResource.query.all())))

    return render_template(
        "learning/resources.html",
        resources=items,
        all_skills=all_skills,
        current_skill=skill_filter,
        current_level=level_filter
    )

@learning_bp.route("/projects")
@login_required
def projects():
    diff_filter = request.args.get("difficulty", "All")
    query = ProjectRecommendation.query
    if diff_filter != "All":
        query = query.filter_by(difficulty=diff_filter)

    items = query.all()
    return render_template("learning/projects.html", projects=items, current_diff=diff_filter)
