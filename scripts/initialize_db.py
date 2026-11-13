"""
SkillBridge AI - Database Initialization & Seeding Script
Creates database tables and populates canonical skills, benchmark career roles,
role requirements, assessment questions, coding challenges, learning resources, and demo data.
Safe to rerun idempotently.
"""

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.extensions import db
from app.models.user import User, Notification
from app.models.skill import Skill, SkillDependency
from app.models.career import CareerRole, RoleRequirement
from app.models.assessment import Assessment, AssessmentQuestion, CodingChallenge, AssessmentAttempt, AssessmentAnswer, CodingSubmission
from app.models.evidence import UserSkillEvidence, SkillGapReport, PortfolioEvidence
from app.models.roadmap import LearningRoadmap, RoadmapMilestone, LearningResource, ProjectRecommendation
from app.models.progress import ProgressSnapshot
from datetime import datetime, timedelta

def seed_database():
    app = create_app("development")
    with app.app_context():
        print("Creating all database tables...", flush=True)
        db.create_all()

        # -------------------------------------------------------------
        # 1. Seed Skills & Prerequisites
        # -------------------------------------------------------------
        ref_tax_path = BASE_DIR / "data" / "reference" / "skills_taxonomy.json"
        taxonomy = {}
        if ref_tax_path.exists():
            with open(ref_tax_path, "r", encoding="utf-8") as f:
                taxonomy = json.load(f)
        
        # Fallback taxonomy if file not yet compiled
        if not taxonomy:
            taxonomy = {
                "Python": {"category": "Programming Languages", "domain": "Core", "prerequisites": [], "importance": "Critical", "description": "Core language for AI, data science, and backend development."},
                "Data Structures & Algorithms": {"category": "Computer Science", "domain": "Core", "prerequisites": ["Python"], "importance": "Critical", "description": "Algorithmic thinking, complexity analysis, trees, and graphs."},
                "SQL": {"category": "Database", "domain": "Core", "prerequisites": [], "importance": "Critical", "description": "Relational query language, schema normalization, and window aggregations."},
                "NumPy": {"category": "Data Science Libraries", "domain": "Data Science", "prerequisites": ["Python"], "importance": "Critical", "description": "High-performance vector operations and linear algebra."},
                "Pandas": {"category": "Data Science Libraries", "domain": "Data Science", "prerequisites": ["Python", "NumPy"], "importance": "Critical", "description": "Tabular data cleaning, transformation, and aggregation."},
                "Data Visualization": {"category": "Data Science", "domain": "Data Science", "prerequisites": ["Python", "Pandas"], "importance": "Medium", "description": "Visualizing distributions, correlations, and business metrics."},
                "Applied Statistics": {"category": "Mathematics", "domain": "Data Science", "prerequisites": ["Python"], "importance": "High", "description": "Hypothesis testing, distributions, regression, and Bayesian theory."},
                "Scikit-Learn": {"category": "Machine Learning", "domain": "AI / ML", "prerequisites": ["Python", "NumPy", "Pandas", "Applied Statistics"], "importance": "Critical", "description": "Supervised & unsupervised ML modeling pipelines."},
                "Machine Learning Modeling": {"category": "Machine Learning", "domain": "AI / ML", "prerequisites": ["Scikit-Learn"], "importance": "Critical", "description": "Model selection, cross-validation, feature importance, and hyperparameter tuning."},
                "Deep Learning": {"category": "Deep Learning", "domain": "AI / ML", "prerequisites": ["Machine Learning Modeling", "NumPy"], "importance": "High", "description": "Neural networks, backpropagation, CNNs, RNNs, and attention."},
                "PyTorch": {"category": "Deep Learning Frameworks", "domain": "AI / ML", "prerequisites": ["Deep Learning", "Python"], "importance": "High", "description": "Dynamic computation graphs and deep learning model training."},
                "Natural Language Processing": {"category": "AI Specialization", "domain": "AI / ML", "prerequisites": ["Deep Learning", "Python"], "importance": "High", "description": "Tokenization, embeddings, Transformers, and LLMs."},
                "Flask / FastAPI": {"category": "Backend Frameworks", "domain": "Software Engineering", "prerequisites": ["Python"], "importance": "High", "description": "Building and deploying production REST APIs."},
                "Docker & Containerization": {"category": "DevOps", "domain": "Infrastructure", "prerequisites": ["Git & Version Control"], "importance": "High", "description": "Containerizing applications for reproducible deployment."},
                "MLOps & Model Deployment": {"category": "MLOps", "domain": "AI / ML", "prerequisites": ["Machine Learning Modeling", "Flask / FastAPI", "Docker & Containerization"], "importance": "High", "description": "Model serving, drift monitoring, CI/CD, and pipeline automation."},
                "Git & Version Control": {"category": "DevOps / Tools", "domain": "Core", "prerequisites": [], "importance": "High", "description": "Branching, PRs, and collaborative version control."},
                "Cloud Computing (AWS/GCP/Azure)": {"category": "Cloud Infrastructure", "domain": "Infrastructure", "prerequisites": ["Docker & Containerization"], "importance": "Medium", "description": "Cloud storage, compute instances, and serverless architectures."}
            }

        print(f"Seeding {len(taxonomy)} skills...", flush=True)
        skill_objects = {}
        for s_name, s_info in taxonomy.items():
            slug = s_name.lower().replace(" ", "-").replace("/", "-").replace("&", "and")
            skill = Skill.query.filter_by(name=s_name).first()
            if not skill:
                skill = Skill(
                    name=s_name,
                    slug=slug,
                    category=s_info.get("category", "General"),
                    domain=s_info.get("domain", "Core"),
                    importance=s_info.get("importance", "High"),
                    description=s_info.get("description", ""),
                    prerequisites_json=json.dumps(s_info.get("prerequisites", []))
                )
                db.session.add(skill)
            skill_objects[s_name] = skill
        db.session.commit()

        # Re-fetch skill objects to get IDs
        skill_objects = {s.name: s for s in Skill.query.all()}

        # -------------------------------------------------------------
        # 2. Seed Benchmark Career Roles & Role Requirements
        # -------------------------------------------------------------
        roles_data = [
            {
                "title": "AI Engineer",
                "slug": "ai-engineer",
                "soc_code": "15-2051.01",
                "domain": "Artificial Intelligence",
                "description": "Designs, trains, and deploys scalable AI models and LLM integrations into production microservices.",
                "salary": "$115,000 - $175,000",
                "growth": "Much Faster than Average (+31%)",
                "reqs": [
                    ("Python", 85, 1.2, True),
                    ("Machine Learning Modeling", 80, 1.2, True),
                    ("Deep Learning", 80, 1.2, True),
                    ("PyTorch", 75, 1.0, True),
                    ("Natural Language Processing", 75, 1.0, False),
                    ("Flask / FastAPI", 75, 1.0, True),
                    ("Docker & Containerization", 70, 0.9, False),
                    ("MLOps & Model Deployment", 75, 1.1, True),
                    ("Data Structures & Algorithms", 70, 0.9, False)
                ]
            },
            {
                "title": "Data Scientist",
                "slug": "data-scientist",
                "soc_code": "15-2051.00",
                "domain": "Data Science & Analytics",
                "description": "Applies statistical modeling, machine learning, and exploratory data analysis to discover business insights.",
                "salary": "$105,000 - $160,000",
                "growth": "Much Faster than Average (+28%)",
                "reqs": [
                    ("Python", 85, 1.1, True),
                    ("Pandas", 85, 1.2, True),
                    ("NumPy", 80, 1.0, True),
                    ("Applied Statistics", 85, 1.2, True),
                    ("Scikit-Learn", 80, 1.1, True),
                    ("Machine Learning Modeling", 80, 1.1, True),
                    ("SQL", 85, 1.2, True),
                    ("Data Visualization", 75, 0.9, False)
                ]
            },
            {
                "title": "Machine Learning Engineer",
                "slug": "machine-learning-engineer",
                "soc_code": "15-2051.01",
                "domain": "AI / ML Systems",
                "description": "Bridges the gap between research models and high-performance production inference pipelines.",
                "salary": "$120,000 - $180,000",
                "growth": "Much Faster than Average (+33%)",
                "reqs": [
                    ("Python", 85, 1.2, True),
                    ("Data Structures & Algorithms", 80, 1.1, True),
                    ("Scikit-Learn", 80, 1.1, True),
                    ("Machine Learning Modeling", 85, 1.2, True),
                    ("Docker & Containerization", 80, 1.1, True),
                    ("MLOps & Model Deployment", 85, 1.2, True),
                    ("Flask / FastAPI", 75, 1.0, False),
                    ("Git & Version Control", 80, 1.0, True)
                ]
            },
            {
                "title": "Software Developer",
                "slug": "software-developer",
                "soc_code": "15-1252.00",
                "domain": "Software Engineering",
                "description": "Develops, tests, and maintains robust application architectures, databases, and client/server systems.",
                "salary": "$95,000 - $150,000",
                "growth": "Faster than Average (+25%)",
                "reqs": [
                    ("Python", 85, 1.2, True),
                    ("Data Structures & Algorithms", 85, 1.2, True),
                    ("SQL", 80, 1.1, True),
                    ("Flask / FastAPI", 80, 1.1, True),
                    ("Git & Version Control", 85, 1.1, True),
                    ("Docker & Containerization", 70, 0.9, False)
                ]
            },
            {
                "title": "Data Analyst",
                "slug": "data-analyst",
                "soc_code": "15-2051.02",
                "domain": "Business Intelligence",
                "description": "Collects, cleans, and models structured data to create analytical dashboards and KPI reports.",
                "salary": "$75,000 - $115,000",
                "growth": "Average (+14%)",
                "reqs": [
                    ("SQL", 90, 1.3, True),
                    ("Python", 75, 1.0, True),
                    ("Pandas", 80, 1.1, True),
                    ("Data Visualization", 85, 1.2, True),
                    ("Applied Statistics", 75, 1.0, True)
                ]
            }
        ]

        print(f"Seeding {len(roles_data)} career roles and requirements...", flush=True)
        for r_info in roles_data:
            role = CareerRole.query.filter_by(title=r_info["title"]).first()
            if not role:
                role = CareerRole(
                    title=r_info["title"],
                    slug=r_info["slug"],
                    soc_code=r_info["soc_code"],
                    domain=r_info["domain"],
                    description=r_info["description"],
                    avg_salary_range=r_info["salary"],
                    growth_outlook=r_info["growth"],
                    benchmark_role=True
                )
                db.session.add(role)
                db.session.flush()

                for s_name, req_prof, weight, is_crit in r_info["reqs"]:
                    s_obj = skill_objects.get(s_name)
                    if s_obj:
                        req = RoleRequirement(
                            role_id=role.id,
                            skill_id=s_obj.id,
                            required_proficiency=req_prof,
                            importance_weight=weight,
                            is_critical=is_crit
                        )
                        db.session.add(req)
        db.session.commit()

        # -------------------------------------------------------------
        # 3. Seed Assessment Questions
        # -------------------------------------------------------------
        q_count = AssessmentQuestion.query.count()
        if q_count == 0:
            print("Seeding Assessment Questions...", flush=True)
            q_file = BASE_DIR / "data" / "processed" / "assessment_questions.json"
            if q_file.exists():
                with open(q_file, "r", encoding="utf-8") as f:
                    q_data = json.load(f)
                for q in q_data:
                    aq = AssessmentQuestion(
                        skill_name=q["skill"],
                        topic=q["topic"],
                        difficulty=q["difficulty"],
                        question_text=q["question"],
                        options_json=json.dumps(q["options"]),
                        correct_option=q["correct_option"],
                        explanation=q["explanation"]
                    )
                    db.session.add(aq)
                db.session.commit()
                print(f"  Loaded {len(q_data)} assessment questions from processed JSON.", flush=True)

        # -------------------------------------------------------------
        # 4. Seed Coding Challenges (MBPP)
        # -------------------------------------------------------------
        c_count = CodingChallenge.query.count()
        if c_count == 0:
            print("Seeding Coding Challenges...", flush=True)
            cc_file = BASE_DIR / "data" / "processed" / "coding_challenges.json"
            if cc_file.exists():
                with open(cc_file, "r", encoding="utf-8") as f:
                    cc_data = json.load(f)
                for c in cc_data[:40]: # Seed top 40 challenges for instant performance
                    cc = CodingChallenge(
                        task_id=c["challenge_id"],
                        title=c["title"],
                        description=c["description"],
                        function_name=c["function_name"],
                        topic=c["topic"],
                        difficulty=c["difficulty"],
                        starter_code=c["starter_code"],
                        reference_solution=c["reference_solution"],
                        test_list_json=json.dumps(c["test_list"]),
                        test_setup_code=c.get("test_setup_code", ""),
                        sample_test=c.get("sample_test", "")
                    )
                    db.session.add(cc)
                db.session.commit()
                print(f"  Loaded {min(len(cc_data), 40)} coding challenges from MBPP JSON.", flush=True)
            else:
                # Built-in fallback coding challenge
                fallback_cc = CodingChallenge(
                    task_id=1,
                    title="Challenge #1: Minimum Cost Path in Matrix",
                    description="Write a function to find the minimum cost path to reach (m, n) from (0, 0) for a given cost matrix cost[][] and a position (m, n).",
                    function_name="min_cost",
                    topic="Dynamic Programming",
                    difficulty="Intermediate",
                    starter_code="def min_cost(cost, m, n):\n    # Write your solution here\n    pass\n",
                    reference_solution="def min_cost(cost, m, n):\n    tc = [[0 for x in range(n+1)] for x in range(m+1)]\n    tc[0][0] = cost[0][0]\n    for i in range(1, m+1):\n        tc[i][0] = tc[i-1][0] + cost[i][0]\n    for j in range(1, n+1):\n        tc[0][j] = tc[0][j-1] + cost[0][j]\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            tc[i][j] = min(tc[i-1][j-1], tc[i-1][j], tc[i][j-1]) + cost[i][j]\n    return tc[m][n]\n",
                    test_list_json=json.dumps(["assert min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) == 8"]),
                    sample_test="assert min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) == 8"
                )
                db.session.add(fallback_cc)
                db.session.commit()

        # -------------------------------------------------------------
        # 5. Seed Learning Resources & Project Recommendations
        # -------------------------------------------------------------
        if LearningResource.query.count() == 0:
            res_file = BASE_DIR / "data" / "reference" / "curated_resources.json"
            if res_file.exists():
                with open(res_file, "r", encoding="utf-8") as f:
                    r_data = json.load(f)
                for r in r_data:
                    lr = LearningResource(
                        skill_name=r["skill"],
                        title=r["title"],
                        resource_type=r.get("type", "Documentation"),
                        level=r.get("level", "Beginner"),
                        url=r["url"],
                        estimated_hours=r.get("estimated_hours", 10),
                        is_free=r.get("is_free", True),
                        description=r.get("description", "")
                    )
                    db.session.add(lr)
                db.session.commit()

        if ProjectRecommendation.query.count() == 0:
            prj_file = BASE_DIR / "data" / "reference" / "curated_projects.json"
            if prj_file.exists():
                with open(prj_file, "r", encoding="utf-8") as f:
                    p_data = json.load(f)
                for p in p_data:
                    pr = ProjectRecommendation(
                        project_code=p["id"],
                        title=p["title"],
                        difficulty=p["difficulty"],
                        target_gap=p["target_gap"],
                        skills_developed_json=json.dumps(p["skills_developed"]),
                        tech_stack_json=json.dumps(p["tech_stack"]),
                        learning_objectives_json=json.dumps(p["learning_objectives"]),
                        deliverables_json=json.dumps(p["expected_deliverables"]),
                        validation_checklist_json=json.dumps(p["validation_checklist"]),
                        portfolio_value=p["portfolio_value"]
                    )
                    db.session.add(pr)
                db.session.commit()

        # -------------------------------------------------------------
        # 6. Seed Demo Candidate User for Immediate Evaluation
        # -------------------------------------------------------------
        demo_email = "sarathkumar@nexora.ai"
        demo_user = User.query.filter_by(email=demo_email).first()
        if not demo_user:
            print("Creating Demo Candidate User (sarathkumar@nexora.ai)...", flush=True)
            demo_user = User(
                email=demo_email,
                full_name="SARATHKUMAR R",
                target_career="AI Engineer",
                study_hours_per_week=12,
                current_education="B.E. Computer Science / AI & ML Specialization",
                bio="Aspiring AI Engineer focused on production machine learning systems, deep learning architectures, and scalable REST APIs."
            )
            demo_user.set_password("SkillBridge2026!")
            db.session.add(demo_user)
            db.session.flush()

            # Seed initial evidences
            py = skill_objects.get("Python")
            sql = skill_objects.get("SQL")
            git = skill_objects.get("Git & Version Control")
            ml = skill_objects.get("Machine Learning Modeling")

            if py:
                db.session.add(UserSkillEvidence(
                    user_id=demo_user.id, skill_id=py.id,
                    claimed_proficiency=85, demonstrated_proficiency=80,
                    evidence_source="Coding Challenge", verification_status="Challenge-Verified",
                    confidence_score=0.92
                ))
            if sql:
                db.session.add(UserSkillEvidence(
                    user_id=demo_user.id, skill_id=sql.id,
                    claimed_proficiency=80, demonstrated_proficiency=75,
                    evidence_source="Technical Assessment", verification_status="Assessment-Verified",
                    confidence_score=0.88
                ))
            if git:
                db.session.add(UserSkillEvidence(
                    user_id=demo_user.id, skill_id=git.id,
                    claimed_proficiency=75, demonstrated_proficiency=75,
                    evidence_source="Resume Extraction", verification_status="Resume-Verified",
                    confidence_score=0.70
                ))
            if ml:
                db.session.add(UserSkillEvidence(
                    user_id=demo_user.id, skill_id=ml.id,
                    claimed_proficiency=70, demonstrated_proficiency=65,
                    evidence_source="Technical Assessment", verification_status="Assessment-Verified",
                    confidence_score=0.82
                ))

            # Add demo portfolio project
            demo_proj = PortfolioEvidence(
                user_id=demo_user.id,
                project_title="End-to-End Customer Churn Prediction Microservice",
                github_url="https://github.com/nexora/customer-churn-mlops",
                live_url="https://churn-predictor.nexora.ai",
                description="Engineered an end-to-end churn prediction pipeline using Scikit-Learn and XGBoost with Docker containerization and FastAPI endpoints. Achieved 0.89 ROC-AUC with PyTest CI/CD.",
                extracted_tech_json=json.dumps(["Python", "Scikit-Learn", "Flask / FastAPI", "Docker & Containerization"]),
                completeness_score=85,
                documentation_rating="Strong (Technical Architecture & Metrics)",
                missing_categories_json=json.dumps([]),
                suggestions_json=json.dumps(["Add Prometheus latency metrics exporter."])
            )
            db.session.add(demo_proj)

            # Add historical progress snapshots
            now = datetime.utcnow()
            for days_ago, score in [(28, 42.0), (21, 51.5), (14, 62.0), (7, 68.5), (0, 74.0)]:
                db.session.add(ProgressSnapshot(
                    user_id=demo_user.id,
                    target_role="AI Engineer",
                    readiness_score=score,
                    verified_skills_count=4,
                    total_gaps_count=5,
                    roadmap_progress_pct=round(score * 0.9),
                    snapshot_date=now - timedelta(days=days_ago)
                ))

            # Welcome notification
            db.session.add(Notification(
                user_id=demo_user.id,
                title="Welcome SARATHKUMAR! 🌟",
                message="Your SkillBridge AI environment is initialized. Your target career is AI Engineer. All 20 intelligence features are ready for demonstration.",
                category="success"
            ))

            db.session.commit()
            print("Demo user created: sarathkumar@nexora.ai / SkillBridge2026!", flush=True)

        print("\nDatabase initialization and seeding completed successfully!", flush=True)

if __name__ == "__main__":
    seed_database()
