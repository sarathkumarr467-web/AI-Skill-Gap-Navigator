import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill
from app.models.career import CareerRole
from app.models.evidence import UserSkillEvidence, PortfolioEvidence, SkillGapReport
from app.models.assessment import AssessmentAttempt, CodingSubmission
from app.models.progress import ProgressSnapshot
from app.services.portfolio_service import PortfolioEvidenceService
from app.services.report_service import PortfolioReportService
from app.services.dependency_service import SkillDependencyGraph
from app.services.readiness_service import JobReadinessService
from app.utils.auth import login_required, get_current_user

portfolio_bp = Blueprint("portfolio", __name__)

@portfolio_bp.route("/portfolio")
@login_required
def index():
    user = get_current_user()
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()
    projects = PortfolioEvidence.query.filter_by(user_id=user.id).order_by(PortfolioEvidence.created_at.desc()).all()
    coding_subs = CodingSubmission.query.filter_by(user_id=user.id, status="PASSED").all()
    assessments = AssessmentAttempt.query.filter_by(user_id=user.id).all()

    return render_template(
        "portfolio/index.html",
        user=user,
        evidences=evidences,
        projects=projects,
        coding_subs=coding_subs,
        assessments=assessments
    )

@portfolio_bp.route("/portfolio/audit", methods=["POST"])
@login_required
def audit_project():
    user = get_current_user()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    github_url = request.form.get("github_url", "").strip()
    live_url = request.form.get("live_url", "").strip()

    if not title or not description:
        flash("Project title and description are required for auditing.", "warning")
        return redirect(url_for("portfolio.index"))

    analysis = PortfolioEvidenceService.analyze_project(
        title=title,
        description=description,
        github_url=github_url,
        live_url=live_url
    )

    proj = PortfolioEvidence(
        user_id=user.id,
        project_title=title,
        github_url=github_url,
        live_url=live_url,
        description=description,
        extracted_tech_json=json.dumps(analysis["extracted_tech"]),
        completeness_score=analysis["completeness_score"],
        documentation_rating=analysis["documentation_rating"],
        missing_categories_json=json.dumps(analysis["missing_categories"]),
        suggestions_json=json.dumps(analysis["suggestions"])
    )
    db.session.add(proj)
    db.session.commit()

    flash(f"Project '{title}' audited successfully! Completeness score: {analysis['completeness_score']}%.", "success")
    return redirect(url_for("portfolio.index"))

@portfolio_bp.route("/portfolio/download-pdf")
@login_required
def download_pdf():
    user = get_current_user()
    role = CareerRole.query.filter_by(title=user.target_career).first() or CareerRole.query.first()
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()
    
    verified_dicts = [e.to_dict() for e in evidences if e.demonstrated_proficiency >= 50]
    coding_dicts = [c.to_dict() for c in CodingSubmission.query.filter_by(user_id=user.id).limit(5).all()]
    project_dicts = [p.to_dict() for p in PortfolioEvidence.query.filter_by(user_id=user.id).limit(4).all()]
    assessment_dicts = [a.to_dict() for a in AssessmentAttempt.query.filter_by(user_id=user.id).limit(5).all()]

    latest_report = SkillGapReport.query.filter_by(user_id=user.id).order_by(SkillGapReport.created_at.desc()).first()
    readiness_score = latest_report.readiness_score if latest_report else 68.0

    pdf_buffer = PortfolioReportService.generate_pdf_report(
        user_name=user.full_name,
        user_email=user.email,
        target_role=role.title,
        readiness_score=readiness_score,
        readiness_category="High Competency" if readiness_score >= 75 else "Developing",
        verified_skills=verified_dicts,
        assessment_history=assessment_dicts,
        coding_submissions=coding_dicts,
        projects=project_dicts
    )

    filename = f"SkillBridge_Portfolio_{user.full_name.replace(' ', '_')}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )

@portfolio_bp.route("/skills/tree")
@login_required
def skill_tree():
    """Feature 3: Skill Dependency Intelligence Graph"""
    graph_service = SkillDependencyGraph()
    cycles_found, cycle_path = graph_service.detect_cycles()
    return render_template(
        "portfolio/tree.html",
        cycles_found=cycles_found,
        cycle_path=cycle_path
    )

@portfolio_bp.route("/api/skills/graph")
@login_required
def api_skill_graph():
    graph_service = SkillDependencyGraph()
    data = graph_service.get_dependency_tree()
    return jsonify(data)

@portfolio_bp.route("/analytics")
@login_required
def analytics():
    """Feature 20: Continuous Skill Intelligence Longitudinal Tracking"""
    user = get_current_user()
    snapshots = ProgressSnapshot.query.filter_by(user_id=user.id).order_by(ProgressSnapshot.snapshot_date.asc()).all()
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()
    attempts = AssessmentAttempt.query.filter_by(user_id=user.id).all()

    return render_template(
        "portfolio/analytics.html",
        user=user,
        snapshots=snapshots,
        evidences=evidences,
        total_attempts=len(attempts)
    )
