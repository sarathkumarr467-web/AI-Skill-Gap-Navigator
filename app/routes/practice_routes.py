from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models.assessment import CodingChallenge, CodingSubmission, MockInterviewSession, MockInterviewResponse
from app.models.evidence import UserSkillEvidence
from app.models.skill import Skill
from app.services.coding_sandbox_service import CodingSandboxService
from app.services.interview_service import MockInterviewCoachService
from app.utils.auth import login_required, get_current_user

practice_bp = Blueprint("practice", __name__)

# -------------------------------------------------------------
# Coding Challenges (MBPP)
# -------------------------------------------------------------
@practice_bp.route("/coding")
@login_required
def coding_index():
    difficulty = request.args.get("difficulty", "All")
    topic = request.args.get("topic", "All")

    query = CodingChallenge.query
    if difficulty != "All":
        query = query.filter_by(difficulty=difficulty)
    if topic != "All":
        query = query.filter_by(topic=topic)

    challenges = query.limit(25).all()
    user = get_current_user()
    recent_subs = CodingSubmission.query.filter_by(user_id=user.id).order_by(CodingSubmission.submitted_at.desc()).limit(6).all()

    return render_template(
        "practice/coding_index.html",
        challenges=challenges,
        recent_subs=recent_subs,
        current_diff=difficulty,
        current_topic=topic
    )

@practice_bp.route("/coding/<int:task_id>")
@login_required
def coding_detail(task_id):
    challenge = CodingChallenge.query.filter_by(task_id=task_id).first_or_404()
    user = get_current_user()
    past_subs = CodingSubmission.query.filter_by(user_id=user.id, challenge_id=challenge.id).order_by(CodingSubmission.submitted_at.desc()).all()

    return render_template(
        "practice/coding_detail.html",
        challenge=challenge,
        past_subs=past_subs
    )

@practice_bp.route("/api/coding/submit", methods=["POST"])
@login_required
def api_coding_submit():
    user = get_current_user()
    data = request.get_json() or {}

    task_id = data.get("task_id")
    code = data.get("code", "").strip()

    challenge = CodingChallenge.query.filter_by(task_id=task_id).first()
    if not challenge:
        return jsonify({"error": "Challenge not found"}), 404

    # Run safe sandboxed execution
    result = CodingSandboxService.execute_challenge(
        user_code=code,
        test_list=challenge.test_list,
        test_setup=challenge.test_setup_code,
        timeout_seconds=3.5
    )

    # Persist submission
    sub = CodingSubmission(
        user_id=user.id,
        challenge_id=challenge.id,
        submitted_code=code,
        passed_tests=result["passed_tests"],
        total_tests=result["total_tests"],
        status=result["status"],
        execution_output=result["output"]
    )
    db.session.add(sub)

    # If passed, upgrade user's Python evidence!
    if result["status"] == "PASSED":
        py_skill = Skill.query.filter_by(name="Python").first()
        if py_skill:
            ev = UserSkillEvidence.query.filter_by(user_id=user.id, skill_id=py_skill.id).first()
            if not ev:
                ev = UserSkillEvidence(
                    user_id=user.id,
                    skill_id=py_skill.id,
                    claimed_proficiency=75,
                    demonstrated_proficiency=70,
                    evidence_source="Coding Challenge",
                    verification_status="Challenge-Verified",
                    confidence_score=0.90
                )
                db.session.add(ev)
            else:
                ev.demonstrated_proficiency = min(max(ev.demonstrated_proficiency, 70) + 2, 95)
                ev.verification_status = "Challenge-Verified"
                ev.confidence_score = min(ev.confidence_score + 0.05, 0.98)

    db.session.commit()
    return jsonify(result)

# -------------------------------------------------------------
# Mock Interview Coach
# -------------------------------------------------------------
@practice_bp.route("/interview")
@login_required
def interview_index():
    user = get_current_user()
    questions = MockInterviewCoachService.get_questions_for_role(user.target_career or "AI Engineer")
    past_sessions = MockInterviewSession.query.filter_by(user_id=user.id).order_by(MockInterviewSession.created_at.desc()).all()

    return render_template(
        "practice/interview.html",
        role=user.target_career,
        questions=questions,
        past_sessions=past_sessions
    )

@practice_bp.route("/api/interview/evaluate", methods=["POST"])
@login_required
def api_interview_evaluate():
    user = get_current_user()
    data = request.get_json() or {}

    question = data.get("question", "")
    q_type = data.get("type", "Technical")
    user_answer = data.get("answer", "")
    
    # Retrieve key concepts for question
    role_questions = MockInterviewCoachService.get_questions_for_role(user.target_career)
    matched_q = next((q for q in role_questions if q["question"] == question), None)
    key_concepts = matched_q.get("key_concepts", []) if matched_q else ["trade-offs", "performance", "architecture"]

    eval_result = MockInterviewCoachService.evaluate_response(
        question=question,
        question_type=q_type,
        user_answer=user_answer,
        key_concepts=key_concepts
    )

    # Save to mock interview session
    import json
    session_obj = MockInterviewSession.query.filter_by(user_id=user.id, target_role=user.target_career).order_by(MockInterviewSession.created_at.desc()).first()
    if not session_obj:
        session_obj = MockInterviewSession(
            user_id=user.id,
            target_role=user.target_career,
            total_questions=1,
            avg_score=eval_result["score"],
            feedback_summary="Initial role practice session."
        )
        db.session.add(session_obj)
        db.session.flush()
    else:
        session_obj.total_questions += 1
        session_obj.avg_score = (session_obj.avg_score + eval_result["score"]) / 2.0

    resp_record = MockInterviewResponse(
        session_id=session_obj.id,
        question_text=question,
        question_type=q_type,
        user_answer=user_answer,
        score=eval_result["score"],
        feedback=eval_result["feedback"],
        missing_concepts_json=json.dumps(eval_result["missing_concepts"])
    )
    db.session.add(resp_record)
    db.session.commit()

    return jsonify(eval_result)
