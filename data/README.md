# SkillBridge AI — Dataset Documentation & Governance Guide

This document describes the sources, licensing, schemas, validation results, and feature mappings for all datasets integrated into **SkillBridge AI**.

---

## 1. Dataset Provenance & Metadata Registry

### 1. Resume Dataset
- **Identifier**: `C0ldSmi1e/resume-dataset`
- **Source**: [Hugging Face Datasets](https://huggingface.co/datasets/C0ldSmi1e/resume-dataset)
- **License**: Apache 2.0
- **Size & Format**: 50.2 MB (Train: 2,257 rows, Eval: 98 rows), CSV
- **Features Powered**:
  - *Feature 5*: Resume Parsing & Text Extraction
  - *ML Task 1*: Resume Career Domain Classification (`models/resume_classifier.joblib`)
- **Key Columns**: `id`, `category`, `skills`, `education`, `experience`, `text`, `html`
- **Data Leakage Check**: Evaluated with strict train/eval segregation; 0 label leakage.

### 2. Resume-Job Fit Dataset
- **Identifier**: `med2425/resume-job-fit-merged-v1`
- **Source**: [Hugging Face Datasets](https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1)
- **License**: Open Source / HF Community
- **Size & Format**: 122.7 MB, Parquet
- **Features Powered**:
  - *Feature 6*: Multi-Job Compatibility Engine
  - *Feature 7*: Explainable Job-Readiness Scoring Engine
- **Intended Use**: Benchmark alignment scoring between candidate profile vectors and job requirements.

### 3. Resume Skill Extractor Dataset
- **Identifier**: `keerthanshetty/resume-skill-extractor-dataset`
- **Source**: [Hugging Face Datasets](https://huggingface.co/datasets/keerthanshetty/resume-skill-extractor-dataset)
- **License**: MIT
- **Size & Format**: 7.45 MB, Parquet
- **Features Powered**:
  - *Feature 2*: Evidence-Based Skill Verification
  - *Feature 4*: Personalized Skill Gap Detection
  - *Feature 5*: Smart Job Description Analyzer
- **Intended Use**: Token-level entity vocabulary for technology skill extraction and synonym mapping.

### 4. Official O*NET Database (28.0 / 29.0)
- **Identifier**: `O*NET Database Text Files`
- **Source**: [O*NET Resource Center](https://www.onetcenter.org/database.html)
- **License**: O*NET Open License / Public Domain (U.S. Department of Labor / Employment and Training Administration)
- **Size & Format**: ~15 MB across 4 files (`Occupation Data.txt`, `Skills.txt`, `Technology Skills.txt`, `Knowledge.txt`), Tab-separated text
- **Features Powered**:
  - *Feature 3*: Skill Dependency Intelligence Graph
  - *Feature 6*: Multi-Job Compatibility Benchmark Profiles
  - *Feature 8*: Career Path Transition Simulator
  - *Feature 9*: Skill Demand Intelligence
- **Intended Use**: Ground-truth occupational taxonomy and standardized technical competencies.

### 5. Google Research MBPP (Mostly Basic Python Problems)
- **Identifier**: `google-research/mbpp`
- **Source**: [Google Research GitHub Repository](https://github.com/google-research/google-research/tree/master/mbpp)
- **License**: Apache 2.0
- **Size & Format**: 0.54 MB, JSONL (974 verified problems)
- **Features Powered**:
  - *Feature 1*: Assessment Bank & Algorithmic Drills
  - *Feature 13*: Adaptive Learning Subsystem
  - *Feature 15*: Coding Skill Analyzer & Safe Subprocess Sandbox
- **Intended Use**: Unit-testable programming problem statements with deterministic input/output assertions.

### 6. Resume-Job Matching Dataset
- **Identifier**: `nonameee12233/job-resume-matching`
- **Source**: [Hugging Face Datasets](https://huggingface.co/datasets/nonameee12233/job-resume-matching)
- **License**: MIT
- **Size & Format**: 18.8 MB (`matches.csv`), CSV
- **Features Powered**:
  - *Feature 6*: Multi-Job Compatibility Engine
  - *Feature 18*: Skill Gap Priority Optimizer
- **Intended Use**: Bipartite candidate-job matching verification.

---

## 2. Dataset Pipeline Commands

All data acquisition, validation, preprocessing, and model training pipelines are fully scripted and reproducible:

```powershell
# 1. Download/Cache datasets
python scripts\download_data.py

# 2. Run data quality & leakage audit
python scripts\validate_data.py

# 3. Preprocess and compile taxonomy & challenge banks
python scripts\preprocess_data.py

# 4. Train real ML models and record evaluation metrics
python scripts\train_models.py

# 5. Initialize & seed SQLite database
python scripts\initialize_db.py
```

---

## 3. Data Governance & Ethical Integrity
- **No Fabricated Labels**: Model metrics, accuracy scores, and class frequencies represent actual held-out evaluations.
- **Privacy First**: Uploaded documents are stripped of PII (emails, phone numbers) before model inference.
- **Non-Guarantee Disclosure**: Job-Readiness indicators are explicitly documented as diagnostic estimates and do not guarantee hiring or placement.
