"""
SkillBridge AI - Explainable Job-Readiness Scoring Engine
Implements Feature 7: Transparent, multi-factor job-readiness indicator with explicit weights,
breakdown, and clear non-guarantee disclosures.
"""

from typing import Dict, List, Any

class JobReadinessService:
    # Documented transparent weights (summing to 100%)
    WEIGHTS = {
        "skill_coverage": 0.40,        # 40%: Breadth of required technical competencies
        "assessment_proficiency": 0.30, # 30%: Rigorous MCQ & technical test scores
        "practical_coding": 0.20,       # 20%: Automated coding challenge problem-solving
        "portfolio_evidence": 0.10      # 10%: Real project artifacts, code repos & docs
    }

    @classmethod
    def calculate_readiness(
        cls,
        coverage_pct: float,
        assessment_avg_pct: float,
        coding_challenges_passed_pct: float,
        portfolio_score_pct: float,
        critical_missing_count: int
    ) -> Dict[str, Any]:
        """
        Calculates explainable readiness score and generates factor breakdowns.
        """
        # Raw weighted score
        w_cov = coverage_pct * cls.WEIGHTS["skill_coverage"]
        w_ass = assessment_avg_pct * cls.WEIGHTS["assessment_proficiency"]
        w_cod = coding_challenges_passed_pct * cls.WEIGHTS["practical_coding"]
        w_prt = portfolio_score_pct * cls.WEIGHTS["portfolio_evidence"]

        raw_total = w_cov + w_ass + w_cod + w_prt

        # Critical penalty: if essential critical skills are completely missing, apply calibration ceiling
        penalty = 0.0
        if critical_missing_count > 0:
            # Dampen readiness by 4% per missing critical competency (max 20%)
            penalty = min(critical_missing_count * 4.0, 20.0)

        final_score = max(0.0, min(100.0, raw_total - penalty))

        # Status category
        if final_score >= 80.0:
            category = "Job-Ready (High Competency)"
            color = "success"
        elif final_score >= 60.0:
            category = "Near Job-Ready (Targeted Practice Needed)"
            color = "primary"
        elif final_score >= 40.0:
            category = "Developing Competency (Active Study)"
            color = "warning"
        else:
            category = "Early Stage (Foundational Skills Missing)"
            color = "danger"

        return {
            "score": round(final_score, 1),
            "category": category,
            "badge_color": color,
            "formula": "Readiness = (Coverage * 40%) + (Assessment * 30%) + (Coding * 20%) + (Portfolio * 10%) - Critical Penalties",
            "weights": {k: int(v * 100) for k, v in cls.WEIGHTS.items()},
            "factors": {
                "skill_coverage": {
                    "raw_value": round(coverage_pct, 1),
                    "weighted_contribution": round(w_cov, 1),
                    "max_weight": 40
                },
                "assessment_proficiency": {
                    "raw_value": round(assessment_avg_pct, 1),
                    "weighted_contribution": round(w_ass, 1),
                    "max_weight": 30
                },
                "practical_coding": {
                    "raw_value": round(coding_challenges_passed_pct, 1),
                    "weighted_contribution": round(w_cod, 1),
                    "max_weight": 20
                },
                "portfolio_evidence": {
                    "raw_value": round(portfolio_score_pct, 1),
                    "weighted_contribution": round(w_prt, 1),
                    "max_weight": 10
                }
            },
            "penalties": {
                "critical_missing_count": critical_missing_count,
                "deduction": round(penalty, 1)
            },
            "disclaimer": "This indicator is an objective, evidence-based diagnostic estimate designed to guide learning priorities. It does not constitute a hiring guarantee or formal employment assessment."
        }
