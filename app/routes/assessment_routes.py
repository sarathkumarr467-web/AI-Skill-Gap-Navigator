from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from app.services.assessment_service import AssessmentService
from app.utils.auth import login_required, get_current_user

assessment_bp = Blueprint("assessment", __name__)

@assessment_bp.route("/assessments")
@login_required
def index():
    user = get_current_user()
    
    # Pre-built domain assessment suites
    domains = [
        {"name": "Python", "desc": "CPython internals, data structures, complexity & concurrency.", "badge": "Core Programming"},
        {"name": "Data Structures & Algorithms", "desc": "Trees, graphs, dynamic programming & sorting complexity.", "badge": "Computer Science"},
        {"name": "Machine Learning Modeling", "desc": "Bias-variance, regularization, evaluation metrics & ensembles.", "badge": "AI / ML"},
        {"name": "SQL", "desc": "Relational algebra, window functions, indexing & aggregation.", "badge": "Databases"},
        {"name": "Deep Learning", "desc": "Backpropagation, neural architectures, transformers & batchnorm.", "badge": "Deep Learning"},
        {"name": "MLOps & Model Deployment", "desc": "Docker, drift detection, CI/CD & model serving APIs.", "badge": "Production Engineering"}
    ]

    recent_attempts = AssessmentAttempt.query.filter_by(user_id=user.id).order_by(AssessmentAttempt.completed_at.desc()).limit(10).all()
    
    # Gather weak topics across all recent attempts
    weak_topics_set = set()
    for att in recent_attempts:
        for wt in att.weak_topics:
            weak_topics_set.add(wt)

    return render_template(
        "assessments/index.html",
        domains=domains,
        recent_attempts=recent_attempts,
        weak_topics=list(weak_topics_set)
    )

@assessment_bp.route("/assessments/take")
@login_required
def take():
    domain = request.args.get("domain", "Python")
    difficulty = request.args.get("difficulty", "All Difficulties")

    questions = AssessmentService.get_questions_for_assessment(domain=domain, difficulty=difficulty, limit=6)
    
    if not questions:
        # Fallback to any questions
        questions = AssessmentQuestion.query.limit(6).all()

    return render_template(
        "assessments/take.html",
        domain=domain,
        difficulty=difficulty,
        questions=questions
    )

@assessment_bp.route("/assessments/submit", methods=["POST"])
@login_required
def submit():
    user = get_current_user()
    domain = request.form.get("domain", "General Technical")
    time_taken = int(request.form.get("time_taken", 60))

    # Extract answers
    user_answers = {}
    for key, val in request.form.items():
        if key.startswith("q_"):
            try:
                q_id = int(key.replace("q_", ""))
                user_answers[q_id] = int(val)
            except ValueError:
                pass

    if not user_answers:
        flash("No answers were recorded. Please select options for each question.", "warning")
        return redirect(url_for("assessment.index"))

    attempt = AssessmentService.evaluate_attempt(
        user_id=user.id,
        domain=domain,
        user_answers=user_answers,
        time_taken_seconds=time_taken
    )

    flash(f"Assessment completed! You scored {attempt.score}/{attempt.total_points} ({attempt.percentage:.1f}%).", "success")
    return redirect(url_for("assessment.result", attempt_id=attempt.id))

@assessment_bp.route("/assessments/result/<int:attempt_id>")
@login_required
def result(attempt_id):
    user = get_current_user()
    attempt = AssessmentAttempt.query.filter_by(id=attempt_id, user_id=user.id).first_or_404()
    return render_template("assessments/result.html", attempt=attempt)
