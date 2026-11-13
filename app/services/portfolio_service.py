"""
SkillBridge AI - Portfolio Evidence Analyzer Service
Implements Feature 16: Analyzes project portfolios, code repositories, and documentation,
evaluates engineering completeness, extracts technologies, and flags missing categories.
"""

import re
from typing import Dict, List, Any
from app.services.skill_extractor import skill_extractor

class PortfolioEvidenceService:
    @staticmethod
    def analyze_project(
        title: str,
        description: str,
        github_url: str = "",
        live_url: str = ""
    ) -> Dict[str, Any]:
        """
        Analyzes project metadata and description.
        Returns extracted tech, completeness score, missing engineering dimensions, and recommendations.
        """
        extracted = skill_extractor.extract_skills_from_text(f"{title} {description}")
        tech_stack = extracted["skills"]

        desc_lower = description.lower()
        missing_categories = []
        strengths = []
        score = 40 # baseline

        # 1. Source control / Repository link
        if github_url and ("github.com" in github_url.lower() or "gitlab.com" in github_url.lower()):
            score += 15
            strengths.append("Verified public Git repository provided.")
        else:
            missing_categories.append("Public Repository Link (GitHub/GitLab)")

        # 2. Live Deployment / Demo
        if live_url and len(live_url) > 10:
            score += 15
            strengths.append("Live deployment / interactive web demo linked.")
        else:
            missing_categories.append("Live Interactive Demo / Cloud Deployment URL")

        # 3. Testing & CI/CD
        if any(w in desc_lower for w in ["pytest", "unittest", "testing", "ci/cd", "github actions", "test suite"]):
            score += 10
            strengths.append("Automated testing and CI/CD pipeline integrated.")
        else:
            missing_categories.append("Automated Test Suite (e.g., PyTest, Unit Testing)")

        # 4. Containerization
        if any(w in desc_lower for w in ["docker", "container", "dockerfile", "docker-compose", "kubernetes"]):
            score += 10
            strengths.append("Containerized execution environment with Docker.")
        else:
            missing_categories.append("Containerization (Dockerfile or Docker Compose)")

        # 5. Documentation & Architecture
        if len(description.split()) >= 60 and any(w in desc_lower for w in ["architecture", "pipeline", "benchmark", "schema", "api"]):
            score += 10
            documentation_rating = "Strong (Technical Architecture & Metrics)"
        elif len(description.split()) >= 30:
            score += 5
            documentation_rating = "Moderate (Basic Overview)"
        else:
            documentation_rating = "Minimal (Needs Detailed Engineering Specs)"
            missing_categories.append("Comprehensive Architectural Documentation")

        completeness_score = min(max(score, 20), 100)

        # Actionable suggestions
        suggestions = []
        for cat in missing_categories:
            suggestions.append(f"Add {cat} to elevate this project from academic proof-of-concept to production portfolio standard.")

        return {
            "title": title,
            "extracted_tech": tech_stack,
            "completeness_score": completeness_score,
            "documentation_rating": documentation_rating,
            "strengths": strengths,
            "missing_categories": missing_categories,
            "suggestions": suggestions
        }
