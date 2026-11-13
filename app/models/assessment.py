from datetime import datetime
import json
from app.extensions import db

class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    domain = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(30), default="Intermediate") # Beginner, Intermediate, Advanced, Adaptive
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship("AssessmentQuestion", backref="assessment", cascade="all, delete-orphan", lazy="joined")
    attempts = db.relationship("AssessmentAttempt", backref="assessment", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "description": self.description,
            "total_questions": len(self.questions)
        }

class AssessmentQuestion(db.Model):
    __tablename__ = "assessment_questions"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=True)
    skill_name = db.Column(db.String(100), nullable=False, index=True)
    topic = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(30), default="Intermediate")
    question_text = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text, nullable=False) # JSON array of 4 options
    correct_option = db.Column(db.Integer, nullable=False) # 0-indexed
    explanation = db.Column(db.Text, default="")

    @property
    def options(self):
        try:
            return json.loads(self.options_json)
        except Exception:
            return []

    def to_dict(self, include_answer=False):
        data = {
            "id": self.id,
            "skill_name": self.skill_name,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "question_text": self.question_text,
            "options": self.options
        }
        if include_answer:
            data["correct_option"] = self.correct_option
            data["explanation"] = self.explanation
        return data

class AssessmentAttempt(db.Model):
    __tablename__ = "assessment_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True)
    domain = db.Column(db.String(80), default="Technical Assessment")
    score = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    skill_breakdown_json = db.Column(db.Text, default="{}") # {skill: {correct: X, total: Y, pct: Z}}
    weak_topics_json = db.Column(db.Text, default="[]")
    time_taken_seconds = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship("AssessmentAnswer", backref="attempt", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def skill_breakdown(self):
        try:
            return json.loads(self.skill_breakdown_json) if self.skill_breakdown_json else {}
        except Exception:
            return {}

    @property
    def weak_topics(self):
        try:
            return json.loads(self.weak_topics_json) if self.weak_topics_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "domain": self.domain,
            "score": self.score,
            "total_points": self.total_points,
            "percentage": round(self.percentage, 1),
            "skill_breakdown": self.skill_breakdown,
            "weak_topics": self.weak_topics,
            "time_taken_seconds": self.time_taken_seconds,
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M")
        }

class AssessmentAnswer(db.Model):
    __tablename__ = "assessment_answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    skill_name = db.Column(db.String(100), default="")
    topic = db.Column(db.String(100), default="")
    selected_option = db.Column(db.Integer, nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class CodingChallenge(db.Model):
    __tablename__ = "coding_challenges"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    function_name = db.Column(db.String(80), default="solution")
    topic = db.Column(db.String(80), default="Python Programming")
    difficulty = db.Column(db.String(30), default="Beginner") # Beginner, Intermediate, Advanced
    starter_code = db.Column(db.Text, nullable=False)
    reference_solution = db.Column(db.Text, default="")
    test_list_json = db.Column(db.Text, nullable=False) # JSON list of assertions
    test_setup_code = db.Column(db.Text, default="")
    sample_test = db.Column(db.String(255), default="")

    submissions = db.relationship("CodingSubmission", backref="challenge", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def test_list(self):
        try:
            return json.loads(self.test_list_json)
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "function_name": self.function_name,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "starter_code": self.starter_code,
            "sample_test": self.sample_test,
            "total_tests": len(self.test_list)
        }

class CodingSubmission(db.Model):
    __tablename__ = "coding_submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("coding_challenges.id", ondelete="CASCADE"), nullable=False)
    submitted_code = db.Column(db.Text, nullable=False)
    passed_tests = db.Column(db.Integer, default=0)
    total_tests = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="PENDING") # PASSED, FAILED, RUNTIME_ERROR, TIMEOUT
    execution_output = db.Column(db.Text, default="")
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "challenge_id": self.challenge_id,
            "challenge_title": self.challenge.title if self.challenge else f"Task #{self.challenge_id}",
            "passed_tests": self.passed_tests,
            "total_tests": self.total_tests,
            "status": self.status,
            "execution_output": self.execution_output,
            "submitted_at": self.submitted_at.strftime("%Y-%m-%d %H:%M")
        }

class MockInterviewSession(db.Model):
    __tablename__ = "mock_interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer, default=0)
    avg_score = db.Column(db.Float, default=0.0)
    feedback_summary = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship("MockInterviewResponse", backref="session", cascade="all, delete-orphan", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "target_role": self.target_role,
            "total_questions": self.total_questions,
            "avg_score": round(self.avg_score, 1),
            "feedback_summary": self.feedback_summary,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "responses": [r.to_dict() for r in self.responses]
        }

class MockInterviewResponse(db.Model):
    __tablename__ = "mock_interview_responses"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("mock_interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default="Technical") # Technical, Conceptual, Scenario
    user_answer = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, default=0.0) # 0 - 100
    feedback = db.Column(db.Text, default="")
    missing_concepts_json = db.Column(db.Text, default="[]")

    @property
    def missing_concepts(self):
        try:
            return json.loads(self.missing_concepts_json) if self.missing_concepts_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "user_answer": self.user_answer,
            "score": round(self.score, 1),
            "feedback": self.feedback,
            "missing_concepts": self.missing_concepts
        }
