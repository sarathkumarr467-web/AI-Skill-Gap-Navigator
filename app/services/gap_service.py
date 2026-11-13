"""
SkillBridge AI - Skill Gap Detection & Priority Optimizer Service
Implements Feature 4 (Personalized Skill Gap Detection) and Feature 18 (Gap Priority Optimizer).
"""

from typing import Dict, List, Any
from app.models.career import CareerRole, RoleRequirement
from app.models.evidence import UserSkillEvidence
from app.services.dependency_service import SkillDependencyGraph

class SkillGapService:
    def __init__(self, taxonomy: Dict[str, Any] = None):
        self.taxonomy = taxonomy or {}
        self.dep_graph = SkillDependencyGraph(self.taxonomy)

    def analyze_gaps(self, user_id: int, role: CareerRole, user_evidences: List[UserSkillEvidence]) -> Dict[str, Any]:
        """
        Compares user's evidence-backed proficiency against target role requirements.
        Distinguishes missing skills, improvement skills, and verified strengths.
        """
        evidence_by_skill = {ev.skill.name: ev for ev in user_evidences if ev.skill}

        critical_gaps = []
        improvement_gaps = []
        verified_skills = []

        total_req_weight = 0.0
        covered_weight = 0.0

        for req in role.requirements:
            s_name = req.skill.name if req.skill else ""
            if not s_name:
                continue

            target_prof = req.required_proficiency
            weight = req.importance_weight
            is_crit = req.is_critical
            total_req_weight += weight

            ev = evidence_by_skill.get(s_name)
            current_prof = ev.demonstrated_proficiency if ev else 0
            verification_status = ev.verification_status if ev else "Unverified"
            evidence_source = ev.evidence_source if ev else "None"

            # Check if covered
            if current_prof >= target_prof:
                covered_weight += weight
                verified_skills.append({
                    "skill": s_name,
                    "category": req.skill.category,
                    "current_proficiency": current_prof,
                    "required_proficiency": target_prof,
                    "verification_status": verification_status,
                    "evidence_source": evidence_source,
                    "status": "Ready"
                })
            elif current_prof > 0:
                deficit = target_prof - current_prof
                covered_weight += weight * (current_prof / target_prof)
                improvement_gaps.append({
                    "skill": s_name,
                    "category": req.skill.category,
                    "current_proficiency": current_prof,
                    "required_proficiency": target_prof,
                    "deficit": deficit,
                    "is_critical": is_crit,
                    "verification_status": verification_status,
                    "priority": self._calculate_priority(deficit, is_crit, s_name),
                    "status": "Needs Improvement"
                })
            else:
                # Completely missing
                deficit = target_prof
                critical_gaps.append({
                    "skill": s_name,
                    "category": req.skill.category,
                    "current_proficiency": 0,
                    "required_proficiency": target_prof,
                    "deficit": deficit,
                    "is_critical": is_crit,
                    "verification_status": "Missing",
                    "priority": self._calculate_priority(deficit, is_crit, s_name),
                    "status": "Missing Competency"
                })

        # Sort gaps by priority descending
        critical_gaps.sort(key=lambda x: x["priority"]["score"], reverse=True)
        improvement_gaps.sort(key=lambda x: x["priority"]["score"], reverse=True)

        coverage_pct = (covered_weight / total_req_weight * 100) if total_req_weight > 0 else 0.0

        return {
            "role_title": role.title,
            "skill_coverage_pct": round(coverage_pct, 1),
            "critical_gaps": critical_gaps,
            "improvement_gaps": improvement_gaps,
            "verified_skills": verified_skills,
            "total_requirements": len(role.requirements),
            "missing_count": len(critical_gaps),
            "improvement_count": len(improvement_gaps),
            "verified_count": len(verified_skills)
        }

    def _calculate_priority(self, deficit: int, is_critical: bool, skill_name: str) -> Dict[str, Any]:
        """
        Explainable Priority Formula:
        Score = (Crit_Weight * 40) + (Deficit% * 30) + (Prereq_Influence * 20) + (Base_Market * 10)
        """
        crit_weight = 1.0 if is_critical else 0.5
        deficit_factor = min(deficit / 100.0, 1.0)
        
        # Check prerequisite influence: does this skill unlock other skills?
        dependents_count = len(self.dep_graph.reverse_adj.get(skill_name, set()))
        prereq_factor = min(dependents_count * 0.3, 1.0)

        raw_score = (crit_weight * 40.0) + (deficit_factor * 30.0) + (prereq_factor * 20.0) + 10.0
        score = round(min(raw_score, 100.0), 1)

        level = "High" if score >= 75 else ("Medium" if score >= 50 else "Low")
        
        reasoning = []
        if is_critical:
            reasoning.append("Directly designated as a core requirement for this career.")
        if deficit >= 50:
            reasoning.append(f"Substantial proficiency deficit of {deficit} points.")
        if dependents_count > 0:
            reasoning.append(f"Prerequisite that unlocks {dependents_count} downstream skill(s).")

        return {
            "score": score,
            "level": level,
            "factors": {
                "criticality": crit_weight,
                "deficit": deficit,
                "dependents_unlocked": dependents_count
            },
            "explanation": " ".join(reasoning) if reasoning else "Standard supplementary skill."
        }
