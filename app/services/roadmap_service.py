"""
SkillBridge AI - Personalized Learning Roadmap Generator
Implements Feature 10: Generates dynamic weekly learning milestones based on
target career, identified gaps, available weekly study hours, and topological prerequisite ordering.
"""

import json
from typing import Dict, List, Any
from app.extensions import db
from app.models.roadmap import LearningRoadmap, RoadmapMilestone, LearningResource
from app.services.dependency_service import SkillDependencyGraph

class RoadmapGeneratorService:
    def __init__(self, taxonomy: Dict[str, Any] = None):
        self.taxonomy = taxonomy or {}
        self.dep_graph = SkillDependencyGraph(self.taxonomy)

    def generate_roadmap(
        self,
        user_id: int,
        target_role: str,
        gaps: List[Dict[str, Any]],
        weekly_hours: int = 10
    ) -> LearningRoadmap:
        """
        Creates a custom learning roadmap tailored to user gaps and study pace.
        """
        # Archive any existing active roadmap for this user
        existing = LearningRoadmap.query.filter_by(user_id=user_id, status="active").all()
        for r in existing:
            r.status = "archived"

        # Determine skills needing study (critical gaps + improvement gaps)
        skills_to_study = [g["skill"] for g in gaps]
        if not skills_to_study:
            skills_to_study = ["Machine Learning Modeling", "MLOps & Model Deployment"]

        # Sort in topological learning order using prerequisite DAG
        ordered_skills = self.dep_graph.get_optimal_learning_sequence(skills_to_study)

        # Estimate weeks per skill based on user's weekly study hours
        milestones_data = []
        current_week = 1

        for skill in ordered_skills:
            # Look up standard hours for this skill
            tax_info = self.taxonomy.get(skill, {})
            est_hours = tax_info.get("estimated_learning_hours", 20)
            
            # Compute weeks required
            weeks_needed = max(1, round(est_hours / max(weekly_hours, 5)))
            
            # Fetch recommended resources for this skill
            resources = LearningResource.query.filter_by(skill_name=skill).limit(2).all()
            res_dicts = [r.to_dict() for r in resources] if resources else [
                {"title": f"Official {skill} Documentation", "url": "https://docs.python.org/3/", "type": "Documentation"}
            ]

            for w_offset in range(weeks_needed):
                part_title = f"Part {w_offset + 1} of {weeks_needed}" if weeks_needed > 1 else "Core Mastery"
                is_reassess = (w_offset == weeks_needed - 1)

                objectives = [
                    f"Master core theoretical principles and standard patterns in {skill}",
                    f"Review real-world industry applications and common architectural pitfalls"
                ]
                
                practice_tasks = [
                    f"Complete 2 hands-on coding drills on {skill}",
                    f"Implement mini-module applying {skill} to target role ({target_role})"
                ]
                
                if is_reassess:
                    practice_tasks.append(f"Take {skill} Reassessment Challenge to verify demonstrated proficiency")

                milestones_data.append({
                    "week_number": current_week,
                    "title": f"Week {current_week}: {skill} ({part_title})",
                    "skill_name": skill,
                    "objectives": objectives,
                    "practice_tasks": practice_tasks,
                    "resources": res_dicts,
                    "is_completed": False
                })
                current_week += 1

        total_weeks = len(milestones_data)

        # Persist new roadmap
        new_roadmap = LearningRoadmap(
            user_id=user_id,
            target_role=target_role,
            total_weeks=total_weeks,
            weekly_hours=weekly_hours,
            current_week=1,
            status="active"
        )
        db.session.add(new_roadmap)
        db.session.flush()

        for m_data in milestones_data:
            milestone = RoadmapMilestone(
                roadmap_id=new_roadmap.id,
                week_number=m_data["week_number"],
                title=m_data["title"],
                skill_name=m_data["skill_name"],
                objectives_json=json.dumps(m_data["objectives"]),
                practice_tasks_json=json.dumps(m_data["practice_tasks"]),
                resources_json=json.dumps(m_data["resources"]),
                is_completed=False
            )
            db.session.add(milestone)

        db.session.commit()
        return new_roadmap
