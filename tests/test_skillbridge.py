"""
SkillBridge AI - Comprehensive Automated Test Suite
Validates critical user workflows, database integrity, ML pipelines,
NLP services, sandboxed coding security, and explainable scoring.
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill
from app.models.career import CareerRole, RoleRequirement
from app.models.assessment import AssessmentQuestion, AssessmentAttempt, CodingChallenge
from app.models.evidence import UserSkillEvidence, SkillGapReport
from app.models.roadmap import LearningRoadmap
from app.services.skill_extractor import skill_extractor
from app.services.dependency_service import SkillDependencyGraph
from app.services.readiness_service import JobReadinessService
from app.services.gap_service import SkillGapService
from app.services.coding_sandbox_service import CodingSandboxService
from app.services.interview_service import MockInterviewCoachService
from app.services.portfolio_service import PortfolioEvidenceService
from app.services.report_service import PortfolioReportService

class SkillBridgeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self._seed_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _seed_test_data(self):
        # 1. Seed Skills
        s1 = Skill(name="Python", slug="python", category="Programming", domain="Core", prerequisites_json="[]")
        s2 = Skill(name="Machine Learning Modeling", slug="machine-learning", category="ML", domain="AI/ML", prerequisites_json='["Python"]')
        s3 = Skill(name="SQL", slug="sql", category="Database", domain="Core", prerequisites_json="[]")
        db.session.add_all([s1, s2, s3])
        db.session.flush()

        # 2. Seed Career Role
        role = CareerRole(
            title="AI Engineer",
            slug="ai-engineer",
            soc_code="15-2051.01",
            domain="AI",
            description="Designs and trains AI models."
        )
        db.session.add(role)
        db.session.flush()

        req1 = RoleRequirement(role_id=role.id, skill_id=s1.id, required_proficiency=80, importance_weight=1.2, is_critical=True)
        req2 = RoleRequirement(role_id=role.id, skill_id=s2.id, required_proficiency=75, importance_weight=1.1, is_critical=True)
        req3 = RoleRequirement(role_id=role.id, skill_id=s3.id, required_proficiency=70, importance_weight=1.0, is_critical=False)
        db.session.add_all([req1, req2, req3])

        # 3. Seed Assessment Question
        q = AssessmentQuestion(
            skill_name="Python",
            topic="Complexity",
            difficulty="Beginner",
            question_text="Dictionary lookup average complexity?",
            options_json=json.dumps(["O(1)", "O(n)", "O(log n)", "O(n^2)"]),
            correct_option=0,
            explanation="Hash tables have O(1) average lookup."
        )
        db.session.add(q)

        # 4. Seed User
        user = User(
            email="test@candidate.com",
            full_name="Test Candidate",
            target_career="AI Engineer",
            study_hours_per_week=10
        )
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

    # ---------------------------------------------------------
    # 1. Startup & User Auth Tests
    # ---------------------------------------------------------
    def test_app_starts_and_home_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SkillBridge AI", response.data)

    def test_user_registration_and_login(self):
        # Register new
        res = self.client.post("/register", data={
            "full_name": "New Candidate",
            "email": "new@nexora.ai",
            "password": "Password123!",
            "target_career": "AI Engineer",
            "study_hours_per_week": "12"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"New Candidate", res.data)

        # Sign out
        self.client.get("/logout", follow_redirects=True)

        # Sign in
        res_login = self.client.post("/login", data={
            "email": "new@nexora.ai",
            "password": "Password123!"
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Dashboard", res_login.data)

    # ---------------------------------------------------------
    # 2. NLP & Skill Extraction Tests
    # ---------------------------------------------------------
    def test_skill_extraction_and_aliases(self):
        sample = "Seeking a developer skilled in Py, Scikit-learn, SQL, and Docker containerization."
        extracted = skill_extractor.extract_skills_from_text(sample)
        self.assertIn("Python", extracted["skills"])
        self.assertIn("Scikit-Learn", extracted["skills"])
        self.assertIn("SQL", extracted["skills"])
        self.assertIn("Docker & Containerization", extracted["skills"])

    def test_job_description_required_vs_preferred(self):
        jd = """
        Minimum Qualifications:
        - Must have strong experience with Python and SQL.
        Preferred Qualifications:
        - Nice to have knowledge of Docker and PyTorch.
        """
        analysis = skill_extractor.analyze_job_description(jd)
        self.assertIn("Python", analysis["required_skills"])
        self.assertIn("Docker & Containerization", analysis["preferred_skills"])

    # ---------------------------------------------------------
    # 3. Skill Dependency DAG & Cycle Detection
    # ---------------------------------------------------------
    def test_dependency_dag_and_cycle_detection(self):
        dag = SkillDependencyGraph({
            "Python": {"prerequisites": []},
            "DSA": {"prerequisites": ["Python"]},
            "ML": {"prerequisites": ["Python", "DSA"]}
        })
        has_cycle, _ = dag.detect_cycles()
        self.assertFalse(has_cycle)

        sequence = dag.get_optimal_learning_sequence(["ML"])
        self.assertEqual(sequence[0], "Python")
        self.assertEqual(sequence[-1], "ML")

    def test_cycle_detection_alert(self):
        cyclic_dag = SkillDependencyGraph({
            "A": {"prerequisites": ["B"]},
            "B": {"prerequisites": ["C"]},
            "C": {"prerequisites": ["A"]}
        })
        has_cycle, path = cyclic_dag.detect_cycles()
        self.assertTrue(has_cycle)
        self.assertGreater(len(path), 0)

    # ---------------------------------------------------------
    # 4. Explainable Job-Readiness Scoring Engine
    # ---------------------------------------------------------
    def test_explainable_readiness_calculation(self):
        res = JobReadinessService.calculate_readiness(
            coverage_pct=80.0,
            assessment_avg_pct=75.0,
            coding_challenges_passed_pct=100.0,
            portfolio_score_pct=70.0,
            critical_missing_count=0
        )
        # 80*0.4(32) + 75*0.3(22.5) + 100*0.2(20) + 70*0.1(7) = 81.5%
        self.assertEqual(res["score"], 81.5)
        self.assertEqual(res["category"], "Job-Ready (High Competency)")

    # ---------------------------------------------------------
    # 5. Sandboxed Coding Challenge & Security Controls
    # ---------------------------------------------------------
    def test_sandboxed_coding_execution_success(self):
        code = "def add(a, b):\n    return a + b\n"
        tests = ["assert add(2, 3) == 5", "assert add(-1, 1) == 0"]
        result = CodingSandboxService.execute_challenge(code, tests)
        self.assertEqual(result["status"], "PASSED")
        self.assertEqual(result["passed_tests"], 2)

    def test_sandboxed_coding_blocks_security_violation(self):
        malicious_code = "import os\nos.system('dir')\ndef add(a, b): return a+b\n"
        result = CodingSandboxService.execute_challenge(malicious_code, ["assert add(1, 2) == 3"])
        self.assertEqual(result["status"], "SECURITY_VIOLATION")
        self.assertIn("Security Alert", result["output"])

    # ---------------------------------------------------------
    # 6. Mock Interview & Portfolio Auditor Tests
    # ---------------------------------------------------------
    def test_mock_interview_evaluation(self):
        q = "How do you detect vanishing gradients?"
        ans = "We use residual connections, batch normalization, and ReLU activations to avoid vanishing gradients."
        eval_res = MockInterviewCoachService.evaluate_response(
            question=q,
            question_type="Technical",
            user_answer=ans,
            key_concepts=["residual connections", "batch normalization", "ReLU"]
        )
        self.assertGreaterEqual(eval_res["score"], 60.0)
        self.assertIn("residual connections", eval_res["identified_concepts"])

    def test_portfolio_auditor_and_pdf_generation(self):
        audit = PortfolioEvidenceService.analyze_project(
            title="ML API",
            description="Trained model with Scikit-learn and pytest tests.",
            github_url="https://github.com/user/ml-api",
            live_url="https://app.com"
        )
        self.assertGreater(audit["completeness_score"], 60)

        # Generate PDF buffer
        pdf_buf = PortfolioReportService.generate_pdf_report(
            user_name="Test Candidate",
            user_email="test@candidate.com",
            target_role="AI Engineer",
            readiness_score=78.5,
            readiness_category="High Competency",
            verified_skills=[{"skill": "Python", "category": "Core", "current_proficiency": 80, "evidence_source": "Coding", "verification_status": "Verified"}],
            assessment_history=[],
            coding_submissions=[],
            projects=[]
        )
        self.assertGreater(pdf_buf.getbuffer().nbytes, 1000)

if __name__ == "__main__":
    unittest.main()
