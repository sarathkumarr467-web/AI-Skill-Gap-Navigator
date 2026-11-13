"""
SkillBridge AI - Skill Extraction & Normalization Service
Extracts, normalizes, and categorizes skills from resume and job description texts.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REF_DIR = BASE_DIR / "data" / "reference"

class SkillExtractorService:
    def __init__(self):
        self.taxonomy = self._load_json(REF_DIR / "skills_taxonomy.json", {})
        self.normalization_map = self._load_json(REF_DIR / "skill_normalization_map.json", {})
        
        # If reference json not yet generated, provide robust built-in fallback
        if not self.taxonomy:
            self.taxonomy = {
                "Python": {"category": "Programming Languages", "domain": "Core"},
                "SQL": {"category": "Database", "domain": "Core"},
                "Data Structures & Algorithms": {"category": "Computer Science", "domain": "Core"},
                "NumPy": {"category": "Data Science Libraries", "domain": "Data Science"},
                "Pandas": {"category": "Data Science Libraries", "domain": "Data Science"},
                "Scikit-Learn": {"category": "Machine Learning", "domain": "AI / ML"},
                "Machine Learning Modeling": {"category": "Machine Learning", "domain": "AI / ML"},
                "Deep Learning": {"category": "Deep Learning", "domain": "AI / ML"},
                "PyTorch": {"category": "Deep Learning Frameworks", "domain": "AI / ML"},
                "Natural Language Processing": {"category": "AI Specialization", "domain": "AI / ML"},
                "Computer Vision": {"category": "AI Specialization", "domain": "AI / ML"},
                "Flask / FastAPI": {"category": "Backend Frameworks", "domain": "Software Engineering"},
                "Docker & Containerization": {"category": "DevOps", "domain": "Infrastructure"},
                "MLOps & Model Deployment": {"category": "MLOps", "domain": "AI / ML"},
                "Git & Version Control": {"category": "DevOps / Tools", "domain": "Core"},
                "HTML / CSS / JavaScript": {"category": "Frontend Development", "domain": "Web Development"},
                "Cloud Computing (AWS/GCP/Azure)": {"category": "Cloud Infrastructure", "domain": "Infrastructure"},
                "Applied Statistics": {"category": "Mathematics", "domain": "Data Science"}
            }
            
        if not self.normalization_map:
            self.normalization_map = {
                "python": "Python", "py": "Python", "sql": "SQL", "mysql": "SQL", "postgres": "SQL",
                "numpy": "NumPy", "pandas": "Pandas", "sklearn": "Scikit-Learn", "scikit-learn": "Scikit-Learn",
                "machine learning": "Machine Learning Modeling", "ml": "Machine Learning Modeling",
                "deep learning": "Deep Learning", "dl": "Deep Learning", "pytorch": "PyTorch", "torch": "PyTorch",
                "tensorflow": "Deep Learning", "keras": "Deep Learning", "nlp": "Natural Language Processing",
                "docker": "Docker & Containerization", "k8s": "Docker & Containerization",
                "fastapi": "Flask / FastAPI", "flask": "Flask / FastAPI", "git": "Git & Version Control",
                "github": "Git & Version Control", "aws": "Cloud Computing (AWS/GCP/Azure)",
                "gcp": "Cloud Computing (AWS/GCP/Azure)", "azure": "Cloud Computing (AWS/GCP/Azure)",
                "data structures": "Data Structures & Algorithms", "algorithms": "Data Structures & Algorithms",
                "dsa": "Data Structures & Algorithms"
            }

    def _load_json(self, path: Path, default_val: Any) -> Any:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return default_val

    def extract_skills_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extracts recognized skills and aliases from text.
        Returns detailed summary: list of canonical skill names, categorized lists, and frequencies.
        """
        if not text or not isinstance(text, str):
            return {"skills": [], "by_category": {}, "frequencies": {}}

        text_lower = text.lower()
        found_skills = {} # canonical_name -> count

        # 1. Check exact canonical skill names
        for canonical, info in self.taxonomy.items():
            pattern = r"\b" + re.escape(canonical.lower()) + r"\b"
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                found_skills[canonical] = matches

        # 2. Check aliases from normalization map
        for alias, canonical in self.normalization_map.items():
            # word boundary search
            pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                found_skills[canonical] = found_skills.get(canonical, 0) + matches

        # Group by category
        by_category = {}
        for skill in found_skills.keys():
            cat = self.taxonomy.get(skill, {}).get("category", "General Technical")
            by_category.setdefault(cat, []).append(skill)

        return {
            "skills": sorted(list(found_skills.keys())),
            "by_category": by_category,
            "frequencies": found_skills
        }

    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """
        Deep analysis of a Job Description:
        - Extracts technical skills, frameworks, languages, tools
        - Distinguishes required vs preferred qualifications
        - Estimates experience level
        """
        extracted = self.extract_skills_from_text(jd_text)
        skills = extracted["skills"]

        # Parse sections for required vs preferred
        required_skills = []
        preferred_skills = []

        lines = jd_text.splitlines()
        current_mode = "required" # default

        for line in lines:
            line_l = line.lower()
            if any(k in line_l for k in ["preferred", "nice to have", "bonus", "plus", "desired", "good to have"]):
                current_mode = "preferred"
            elif any(k in line_l for k in ["required", "minimum", "qualifications", "must have", "requirements", "essential"]):
                current_mode = "required"

            # Check skills in this line using line extraction
            line_extracted = self.extract_skills_from_text(line)["skills"]
            for s in line_extracted:
                if current_mode == "preferred" and s not in preferred_skills:
                    preferred_skills.append(s)
                elif current_mode == "required" and s not in required_skills:
                    required_skills.append(s)

        # Fallback if partitioning was inconclusive
        if not required_skills and not preferred_skills:
            required_skills = skills
        elif not required_skills and preferred_skills:
            required_skills = [s for s in skills if s not in preferred_skills]

        # Experience level detection
        exp_level = "Entry-Level / Junior (0-2 years)"
        jd_lower = jd_text.lower()
        if re.search(r"\b(senior|lead|principal|staff|architect)\b", jd_lower) or re.search(r"\b(5\+|6\+|7\+|8\+|10\+)\s*years?\b", jd_lower):
            exp_level = "Senior (5+ years)"
        elif re.search(r"\b(mid|intermediate|experienced|3\+|4\+)\s*years?\b", jd_lower):
            exp_level = "Mid-Level (2-5 years)"

        return {
            "all_skills": skills,
            "required_skills": required_skills if required_skills else skills,
            "preferred_skills": preferred_skills,
            "by_category": extracted["by_category"],
            "experience_level": exp_level,
            "total_skills_found": len(skills)
        }

# Global singleton
skill_extractor = SkillExtractorService()
