import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models.career import CareerRole
from app.models.evidence import UserSkillEvidence, SkillGapReport
from app.services.gap_service import SkillGapService
from app.services.compatibility_service import CompatibilityService
from app.services.career_simulator_service import CareerSimulatorService
from app.services.readiness_service import JobReadinessService
from app.utils.auth import login_required, get_current_user

gap_bp = Blueprint("gap", __name__)

@gap_bp.route("/gap-analysis")
@login_required
def gap_analysis():
    user = get_current_user()
    role_id = request.args.get("role_id", type=int)

    if role_id:
        role = CareerRole.query.get(role_id)
    else:
        role = CareerRole.query.filter_by(title=user.target_career).first() or CareerRole.query.first()

    all_roles = CareerRole.query.all()
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()

    # Run gap analysis
    gap_service = SkillGapService()
    analysis = gap_service.analyze_gaps(user.id, role, evidences)

    # Compute overall readiness score
    avg_assessment = 70.0 if any(e.evidence_source == "Technical Assessment" for e in evidences) else 0.0
    coding_count = user.coding_submissions.count()
    coding_pct = 80.0 if coding_count > 0 else 0.0

    readiness = JobReadinessService.calculate_readiness(
        coverage_pct=analysis["skill_coverage_pct"],
        assessment_avg_pct=avg_assessment,
        coding_challenges_passed_pct=coding_pct,
        portfolio_score_pct=60.0 if user.portfolio_items.count() > 0 else 10.0,
        critical_missing_count=len(analysis["critical_gaps"])
    )

    # Save snapshot report to database
    report = SkillGapReport(
        user_id=user.id,
        role_id=role.id,
        role_title=role.title,
        readiness_score=readiness["score"],
        skill_coverage_pct=analysis["skill_coverage_pct"],
        critical_gaps_json=json.dumps(analysis["critical_gaps"]),
        improvement_gaps_json=json.dumps(analysis["improvement_gaps"]),
        verified_skills_json=json.dumps(analysis["verified_skills"]),
        readiness_breakdown_json=json.dumps(readiness["factors"]),
        recommendations_json=json.dumps([g["skill"] for g in analysis["critical_gaps"][:4]])
    )
    db.session.add(report)
    db.session.commit()

    return render_template(
        "gap/report.html",
        role=role,
        all_roles=all_roles,
        analysis=analysis,
        readiness=readiness,
        report=report
    )

@gap_bp.route("/compatibility")
@login_required
def compatibility():
    user = get_current_user()
    roles = CareerRole.query.all()
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()

    comparison = CompatibilityService.compare_multiple_roles(roles, evidences)
    return render_template("gap/compatibility.html", comparison=comparison)

@gap_bp.route("/career-simulator")
@login_required
def simulator():
    user = get_current_user()
    roles = CareerRole.query.all()
    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()

    current_role_title = request.args.get("current_role", "Software Developer")
    target_role_title = request.args.get("target_role", user.target_career or "AI Engineer")

    curr_role = CareerRole.query.filter_by(title=current_role_title).first() or roles[0]
    tgt_role = CareerRole.query.filter_by(title=target_role_title).first() or roles[1]

    transition = CareerSimulatorService.simulate_path_transition(
        curr_role, tgt_role, evidences, weekly_study_hours=user.study_hours_per_week
    )

    # Skills available to boost for What-If simulator
    available_skills = [r.skill.name for r in tgt_role.requirements if r.skill]

    return render_template(
        "gap/simulator.html",
        roles=roles,
        current_role=curr_role,
        target_role=tgt_role,
        transition=transition,
        available_skills=available_skills,
        study_hours=user.study_hours_per_week
    )

@gap_bp.route("/api/simulate-what-if", methods=["POST"])
@login_required
def api_simulate_what_if():
    user = get_current_user()
    data = request.get_json() or {}

    target_role_title = data.get("target_role", user.target_career)
    role = CareerRole.query.filter_by(title=target_role_title).first()
    if not role:
        return jsonify({"error": "Role not found"}), 404

    skills_to_boost = data.get("boosted_skills", [])
    weekly_hours = int(data.get("weekly_hours", user.study_hours_per_week))
    weeks = int(data.get("weeks", 8))

    evidences = UserSkillEvidence.query.filter_by(user_id=user.id).all()

    simulation = CareerSimulatorService.run_what_if_simulation(
        target_role=role,
        user_evidences=evidences,
        selected_skills_to_boost=skills_to_boost,
        additional_study_hours_per_week=weekly_hours,
        simulation_weeks=weeks
    )

    return jsonify(simulation)
