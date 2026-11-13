"""
SkillBridge AI - Multi-Job Compatibility Engine
Implements Feature 6: Evaluates user's demonstrated competencies across multiple career roles,
providing radar charts, gap overlap, and transferable strength matrices.
"""

from typing import Dict, List, Any
from app.models.career import CareerRole
from app.models.evidence import UserSkillEvidence

class CompatibilityService:
    @staticmethod
    def compare_multiple_roles(roles: List[CareerRole], user_evidences: List[UserSkillEvidence]) -> List[Dict[str, Any]]:
        """
        Computes compatibility match across all target roles.
        """
        evidence_by_skill = {ev.skill.name: ev.demonstrated_proficiency for ev in user_evidences if ev.skill}

        results = []
        for role in roles:
            total_reqs = len(role.requirements)
            if total_reqs == 0:
                continue

            matched_skills = []
            partial_skills = []
            missing_skills = []

            total_weight = 0.0
            earned_weight = 0.0

            for req in role.requirements:
                s_name = req.skill.name if req.skill else ""
                if not s_name:
                    continue

                w = req.importance_weight
                target_p = req.required_proficiency
                total_weight += w

                user_p = evidence_by_skill.get(s_name, 0)
                if user_p >= target_p:
                    earned_weight += w
                    matched_skills.append(s_name)
                elif user_p > 0:
                    earned_weight += w * (user_p / target_p)
                    partial_skills.append({
                        "skill": s_name,
                        "current": user_p,
                        "required": target_p
                    })
                else:
                    missing_skills.append({
                        "skill": s_name,
                        "required": target_p,
                        "is_critical": req.is_critical
                    })

            match_pct = (earned_weight / total_weight * 100) if total_weight > 0 else 0.0

            results.append({
                "role_id": role.id,
                "role_title": role.title,
                "domain": role.domain,
                "avg_salary": role.avg_salary_range,
                "growth_outlook": role.growth_outlook,
                "compatibility_score": round(match_pct, 1),
                "matched_count": len(matched_skills),
                "partial_count": len(partial_skills),
                "missing_count": len(missing_skills),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "status": "Strong Match" if match_pct >= 75 else ("Viable Transition" if match_pct >= 50 else "High Skill Gap")
            })

        # Sort highest compatibility first
        results.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return results
