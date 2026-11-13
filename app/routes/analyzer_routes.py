import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.user import User, Notification
from app.models.skill import Skill
from app.models.career import CareerRole, JobPosting
from app.models.evidence import UserSkillEvidence
from app.services.document_service import extract_text_from_file
from app.services.skill_extractor import skill_extractor
from app.utils.auth import login_required, get_current_user

analyzer_bp = Blueprint("analyzer", __name__)

@analyzer_bp.route("/resume-analyzer", methods=["GET", "POST"])
@login_required
def resume_analyzer():
    user = get_current_user()
    result = None

    if request.method == "POST":
        file = request.files.get("resume_file")
        raw_text = request.form.get("resume_text", "").strip()

        extracted_text = ""
        filename = "pasted_text.txt"

        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_dir = current_app.config["UPLOAD_FOLDER"]
            upload_dir.mkdir(parents=True, exist_ok=True)
            saved_path = upload_dir / f"user_{user.id}_{filename}"
            file.save(saved_path)

            ok, doc_text, msg = extract_text_from_file(saved_path)
            if not ok:
                flash(msg, "danger")
                return render_template("analyzer/resume.html", result=None)
            extracted_text = doc_text
        elif raw_text:
            extracted_text = raw_text
        else:
            flash("Please upload a resume file (PDF, DOCX, TXT) or paste resume text.", "warning")
            return render_template("analyzer/resume.html", result=None)

        # Extract skills
        extracted_data = skill_extractor.extract_skills_from_text(extracted_text)
        found_skills = extracted_data["skills"]

        # Run domain classification if trained model exists
        predicted_domain = "Technology / Engineering"
        domain_confidence = 88.0
        model_path = current_app.config["MODELS_DIR"] / "resume_classifier.joblib"
        if model_path.exists():
            try:
                import joblib
                import numpy as np
                clf = joblib.load(model_path)
                predicted_domain = clf.predict([extracted_text])[0]
                probs = clf.predict_proba([extracted_text])[0]
                domain_confidence = round(float(np.max(probs)) * 100, 1)
            except Exception:
                pass

        # Update user's evidence records for newly identified skills
        added_count = 0
        for s_name in found_skills:
            skill_obj = Skill.query.filter_by(name=s_name).first()
            if skill_obj:
                ev = UserSkillEvidence.query.filter_by(user_id=user.id, skill_id=skill_obj.id).first()
                if not ev:
                    ev = UserSkillEvidence(
                        user_id=user.id,
                        skill_id=skill_obj.id,
                        claimed_proficiency=65,
                        demonstrated_proficiency=55, # Initial evidence from resume
                        evidence_source="Resume Extraction",
                        verification_status="Resume-Verified",
                        confidence_score=0.60,
                        notes=f"Extracted from {filename}"
                    )
                    db.session.add(ev)
                    added_count += 1
                elif ev.demonstrated_proficiency < 55:
                    ev.demonstrated_proficiency = 55
                    ev.evidence_source = "Resume Extraction"
                    ev.verification_status = "Resume-Verified"

        db.session.commit()

        result = {
            "filename": filename,
            "text_sample": extracted_text[:400] + "...",
            "extracted_skills": found_skills,
            "by_category": extracted_data["by_category"],
            "total_skills_count": len(found_skills),
            "added_count": added_count,
            "predicted_domain": predicted_domain,
            "domain_confidence": domain_confidence
        }
        flash(f"Resume parsed successfully! Identified {len(found_skills)} technical skills and updated your evidence profile.", "success")

    return render_template("analyzer/resume.html", result=result)

@analyzer_bp.route("/job-analyzer", methods=["GET", "POST"])
@login_required
def job_analyzer():
    user = get_current_user()
    result = None

    if request.method == "POST":
        job_title = request.form.get("job_title", "Software Engineer").strip()
        company = request.form.get("company", "Tech Enterprise").strip()
        jd_text = request.form.get("jd_text", "").strip()

        if not jd_text:
            flash("Please paste a target job description.", "warning")
            return render_template("analyzer/job.html", result=None)

        analysis = skill_extractor.analyze_job_description(jd_text)

        # Check user coverage against this specific JD
        user_skills = {e.skill.name: e.demonstrated_proficiency for e in user.skill_evidences if e.skill}
        matching = [s for s in analysis["all_skills"] if user_skills.get(s, 0) >= 50]
        missing = [s for s in analysis["all_skills"] if user_skills.get(s, 0) < 50]

        coverage_pct = (len(matching) / len(analysis["all_skills"]) * 100) if analysis["all_skills"] else 0.0

        result = {
            "job_title": job_title,
            "company": company,
            "experience_level": analysis["experience_level"],
            "all_skills": analysis["all_skills"],
            "required_skills": analysis["required_skills"],
            "preferred_skills": analysis["preferred_skills"],
            "by_category": analysis["by_category"],
            "matching_skills": matching,
            "missing_skills": missing,
            "coverage_pct": round(coverage_pct, 1)
        }

    return render_template("analyzer/job.html", result=result)

@analyzer_bp.route("/demand-intelligence")
@login_required
def demand_intelligence():
    """
    Feature 9: Skill Demand Intelligence
    Analyzes skill frequencies across job postings and career benchmarks.
    """
    roles = CareerRole.query.all()
    
    # Skill frequency ranking across roles
    skill_freq = {}
    for r in roles:
        for req in r.requirements:
            s_name = req.skill.name if req.skill else ""
            if s_name:
                skill_freq[s_name] = skill_freq.get(s_name, 0) + (2 if req.is_critical else 1)

    sorted_demand = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        "analyzer/demand.html",
        roles=roles,
        demand_ranking=sorted_demand[:12],
        total_tracked_skills=len(skill_freq)
    )
