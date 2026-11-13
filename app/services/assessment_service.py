"""
SkillBridge AI - Assessment & Adaptive Learning Service
Implements Feature 1 (Skill Assessment) and Feature 13 (Adaptive Learning Engine).
"""

from typing import Dict, List, Any
from app.models.assessment import AssessmentQuestion, AssessmentAttempt, AssessmentAnswer
from app.models.evidence import UserSkillEvidence
from app.models.skill import Skill
from app.extensions import db

class AssessmentService:
    @staticmethod
    def get_questions_for_assessment(domain: str = None, difficulty: str = None, limit: int = 10) -> List[AssessmentQuestion]:
        """Fetches questions matching domain or difficulty."""
        query = AssessmentQuestion.query
        if domain and domain != "All Domains":
            query = query.filter_by(skill_name=domain)
        if difficulty and difficulty != "All Difficulties" and difficulty != "Adaptive":
            query = query.filter_by(difficulty=difficulty)
        return query.limit(limit).all()

    @staticmethod
    def evaluate_attempt(
        user_id: int,
        domain: str,
        user_answers: Dict[int, int], # question_id -> selected_option
        time_taken_seconds: int = 120
    ) -> AssessmentAttempt:
        """
        Evaluates submitted MCQ answers, computes topic-level breakdowns,
        identifies weak topics, and updates UserSkillEvidence.
        """
        question_ids = list(user_answers.keys())
        questions = AssessmentQuestion.query.filter(AssessmentQuestion.id.isin(question_ids)).all()
        q_map = {q.id: q for q in questions}

        total_points = len(questions)
        correct_count = 0
        skill_stats = {} # skill -> {correct, total}
        weak_topics = set()

        attempt = AssessmentAttempt(
            user_id=user_id,
            domain=domain,
            total_points=total_points,
            time_taken_seconds=time_taken_seconds
        )
        db.session.add(attempt)
        db.session.flush()

        for q_id, selected_opt in user_answers.items():
            q = q_map.get(int(q_id))
            if not q:
                continue

            is_correct = (selected_opt == q.correct_option)
            if is_correct:
                correct_count += 1

            s_name = q.skill_name
            skill_stats.setdefault(s_name, {"correct": 0, "total": 0})
            skill_stats[s_name]["total"] += 1
            if is_correct:
                skill_stats[s_name]["correct"] += 1
            else:
                weak_topics.add(q.topic)

            ans_record = AssessmentAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                skill_name=s_name,
                topic=q.topic,
                selected_option=selected_opt,
                correct_option=q.correct_option,
                is_correct=is_correct
            )
            db.session.add(ans_record)

        pct = (correct_count / total_points * 100) if total_points > 0 else 0.0
        attempt.score = correct_count
        attempt.percentage = pct

        # Format skill breakdown
        breakdown = {}
        for s_name, stats in skill_stats.items():
            s_pct = round((stats["correct"] / stats["total"]) * 100, 1)
            breakdown[s_name] = {
                "correct": stats["correct"],
                "total": stats["total"],
                "percentage": s_pct
            }
            
            # Update or create UserSkillEvidence with demonstrated proficiency
            skill_obj = Skill.query.filter_by(name=s_name).first()
            if skill_obj:
                ev = UserSkillEvidence.query.filter_by(user_id=user_id, skill_id=skill_obj.id).first()
                if not ev:
                    ev = UserSkillEvidence(
                        user_id=user_id,
                        skill_id=skill_obj.id,
                        claimed_proficiency=s_pct,
                        demonstrated_proficiency=int(s_pct),
                        evidence_source="Technical Assessment",
                        verification_status="Assessment-Verified" if s_pct >= 60 else "Needs Improvement",
                        confidence_score=0.85
                    )
                    db.session.add(ev)
                else:
                    # Update demonstrated proficiency with exponential moving average
                    ev.demonstrated_proficiency = int(round(ev.demonstrated_proficiency * 0.4 + s_pct * 0.6))
                    ev.evidence_source = "Technical Assessment"
                    if ev.demonstrated_proficiency >= 60:
                        ev.verification_status = "Assessment-Verified"
                    ev.confidence_score = min(ev.confidence_score + 0.15, 0.95)

        import json
        attempt.skill_breakdown_json = json.dumps(breakdown)
        attempt.weak_topics_json = json.dumps(list(weak_topics))

        db.session.commit()
        return attempt
