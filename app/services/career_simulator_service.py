"""
SkillBridge AI - Career Path Simulator & What-If Engine
Implements Feature 8 (Career Path Simulator) and Feature 19 (What-If Career Simulator).
"""

from typing import Dict, List, Set, Any
from app.models.career import CareerRole
from app.models.evidence import UserSkillEvidence
from app.services.readiness_service import JobReadinessService

class CareerSimulatorService:
    @staticmethod
    def simulate_path_transition(
        current_role: CareerRole,
        target_role: CareerRole,
        user_evidences: List[UserSkillEvidence],
        weekly_study_hours: int = 10
    ) -> Dict[str, Any]:
        """
        Feature 8: Compares current role requirements with target role requirements,
        identifying transferable skills, delta competencies, and estimated transition hours.
        """
        current_reqs = {r.skill.name: r for r in current_role.requirements if r.skill}
        target_reqs = {r.skill.name: r for r in target_role.requirements if r.skill}
        user_skills = {ev.skill.name: ev.demonstrated_proficiency for ev in user_evidences if ev.skill}

        # Shared competencies
        shared_skills = set(current_reqs.keys()).intersection(set(target_reqs.keys()))
        
        # Transferable skills: shared skills where user already has proficiency > 50
        transferable = [s for s in shared_skills if user_skills.get(s, 0) >= 50]
        
        # Target role-specific gaps: skills in target role not in current role OR user proficiency < target
        role_specific_gaps = []
        total_effort_hours = 0

        for s_name, req in target_reqs.items():
            user_p = user_skills.get(s_name, 0)
            req_p = req.required_proficiency
            if user_p < req_p:
                deficit = req_p - user_p
                # Standard assumption: ~0.4 study hours per proficiency point
                skill_hours = round(deficit * 0.4)
                total_effort_hours += skill_hours
                role_specific_gaps.append({
                    "skill": s_name,
                    "category": req.skill.category if req.skill else "General",
                    "current_proficiency": user_p,
                    "target_proficiency": req_p,
                    "deficit": deficit,
                    "estimated_hours": skill_hours,
                    "is_critical": req.is_critical
                })

        estimated_weeks = max(1, round(total_effort_hours / max(weekly_study_hours, 5)))

        return {
            "current_role": current_role.title,
            "target_role": target_role.title,
            "shared_skills_count": len(shared_skills),
            "shared_skills": list(shared_skills),
            "transferable_strengths": transferable,
            "role_specific_gaps": role_specific_gaps,
            "total_effort_hours": total_effort_hours,
            "weekly_study_hours": weekly_study_hours,
            "estimated_weeks": estimated_weeks,
            "transition_difficulty": "Low" if total_effort_hours < 50 else ("Moderate" if total_effort_hours < 120 else "High")
        }

    @staticmethod
    def run_what_if_simulation(
        target_role: CareerRole,
        user_evidences: List[UserSkillEvidence],
        selected_skills_to_boost: List[str],
        additional_study_hours_per_week: int = 10,
        simulation_weeks: int = 8
    ) -> Dict[str, Any]:
        """
        Feature 19: Simulates the quantitative impact of learning specific skills
        over an N-week period on the explainable job-readiness score.
        """
        base_skills = {ev.skill.name: ev.demonstrated_proficiency for ev in user_evidences if ev.skill}
        
        # Calculate baseline metrics
        total_weight = sum(r.importance_weight for r in target_role.requirements if r.skill)
        
        def compute_score_for_profile(skill_dict):
            earned = 0.0
            crit_missing = 0
            for r in target_role.requirements:
                if not r.skill:
                    continue
                p = skill_dict.get(r.skill.name, 0)
                if p >= r.required_proficiency:
                    earned += r.importance_weight
                elif p > 0:
                    earned += r.importance_weight * (p / r.required_proficiency)
                else:
                    if r.is_critical:
                        crit_missing += 1
            cov = (earned / total_weight * 100) if total_weight > 0 else 0.0
            return JobReadinessService.calculate_readiness(
                coverage_pct=cov,
                assessment_avg_pct=min(cov * 0.9, 100),
                coding_challenges_passed_pct=min(cov * 0.8, 100),
                portfolio_score_pct=60.0,
                critical_missing_count=crit_missing
            )

        baseline_result = compute_score_for_profile(base_skills)

        # Simulate boosted skills
        simulated_skills = dict(base_skills)
        total_simulated_hours = additional_study_hours_per_week * simulation_weeks
        hours_per_skill = total_simulated_hours / max(len(selected_skills_to_boost), 1)

        for s in selected_skills_to_boost:
            current_val = simulated_skills.get(s, 0)
            # Assumption: ~2.5 points per hour of focused practice (diminishing above 80)
            gain = min(round(hours_per_skill * 2.5), 85 - current_val)
            simulated_skills[s] = min(max(current_val + max(gain, 15), 65), 95)

        simulated_result = compute_score_for_profile(simulated_skills)
        score_gain = round(simulated_result["score"] - baseline_result["score"], 1)

        return {
            "target_role": target_role.title,
            "simulation_weeks": simulation_weeks,
            "weekly_study_hours": additional_study_hours_per_week,
            "total_study_hours": total_simulated_hours,
            "boosted_skills": selected_skills_to_boost,
            "baseline_readiness": baseline_result["score"],
            "simulated_readiness": simulated_result["score"],
            "projected_gain": max(0.0, score_gain),
            "baseline_category": baseline_result["category"],
            "simulated_category": simulated_result["category"],
            "explanation": f"Investing {total_simulated_hours} total hours across {len(selected_skills_to_boost)} target competency areas is projected to raise readiness by {max(0.0, score_gain)} points under standard deliberate practice assumptions."
        }
