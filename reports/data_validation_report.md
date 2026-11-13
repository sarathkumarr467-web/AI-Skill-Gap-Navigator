# SkillBridge AI - Dataset Validation & Audit Report

> **Project**: SkillBridge AI - Intelligent Skill Gap Analysis & Career Intelligence Platform  
> **Team**: NEXORA | **Lead**: SARATHKUMAR R  
> **Generated**: Automated Data Quality Pipeline  

## Executive Summary
This audit validates the schema, missing values, duplicates, class distributions, and data leakage across all 6 acquired datasets in compliance with the Non-Negotiable Implementation Rules.

| Dataset | Source / License | Rows / Records | Missing Values | Status |
| :--- | :--- | :--- | :--- | :--- |
| **C0ldSmi1e/resume-dataset** | Apache-2.0 | 2257 | 0 | `VALIDATED` |
| **med2425/resume-job-fit-merged-v1** | Open Source / HF Community | 40009 | 0 | `VALIDATED` |
| **keerthanshetty/resume-skill-extractor-dataset** | MIT | 3050 | 0 | `VALIDATED` |
| **Official O*NET Database (28.0/29.0)** | O*NET Open License / Public Domain (U.S. Department of Labor) | Multiple Files | 0 | `VALIDATED` |
| **nonameee12233/job-resume-matching** | MIT | Multiple Files | 0 | `PARTIAL` |
| **Google Research MBPP (Mostly Basic Python Problems)** | Apache-2.0 | 974 | 0 | `VALIDATED` |

## Detailed Audits by Dataset
### C0ldSmi1e/resume-dataset
- **Source URL**: https://huggingface.co/datasets/C0ldSmi1e/resume-dataset
- **License**: Apache-2.0
- **Intended Use**: Resume text categorization and domain classification
- **SkillBridge AI Features Powered**: Feature 4 (Skill Gap), Feature 5 (Resume Parser), Feature 6 (Multi-Job Compatibility)
- **Audit Status**: `VALIDATED`
- **Data Leakage Check**: 0 overlapping records found between train and eval (0.0%)
- **Top Categories / Classes**: `{"BUSINESS-DEVELOPMENT": 118, "FINANCE": 118, "ACCOUNTANT": 117, "FITNESS": 116, "AVIATION": 116, "HEALTHCARE": 115, "CONSULTANT": 115, "SALES": 114, "CHEF": 114, "ENGINEERING": 114}`

### med2425/resume-job-fit-merged-v1
- **Source URL**: https://huggingface.co/datasets/med2425/resume-job-fit-merged-v1
- **License**: Open Source / HF Community
- **Intended Use**: Resume-Job description alignment and fit scoring
- **SkillBridge AI Features Powered**: Feature 6 (Multi-Job Compatibility), Feature 7 (Job-Readiness Indicator)
- **Audit Status**: `VALIDATED`

### keerthanshetty/resume-skill-extractor-dataset
- **Source URL**: https://huggingface.co/datasets/keerthanshetty/resume-skill-extractor-dataset
- **License**: MIT
- **Intended Use**: Token-level and entity-level skill extraction from resume text
- **SkillBridge AI Features Powered**: Feature 2 (Skill Verification), Feature 4 (Skill Gap Detection), Feature 5 (JD Analyzer)
- **Audit Status**: `VALIDATED`

### Official O*NET Database (28.0/29.0)
- **Source URL**: https://www.onetcenter.org/database.html
- **License**: O*NET Open License / Public Domain (U.S. Department of Labor)
- **Intended Use**: Standardized career taxonomy, skills taxonomy, technology tools, and prerequisite structure
- **SkillBridge AI Features Powered**: Feature 3 (Skill Dependency), Feature 6 (Role Compatibility), Feature 8 (Career Simulator), Feature 9 (Skill Demand)
- **Audit Status**: `VALIDATED`
- **Component Tables**:
  - `Occupation Data.txt`: 1016 rows, columns: ['O*NET-SOC Code', 'Title', 'Description']
  - `Skills.txt`: 61110 rows, columns: ['O*NET-SOC Code', 'Element ID', 'Element Name', 'Scale ID', 'Data Value']
  - `Technology Skills.txt`: 32384 rows, columns: ['O*NET-SOC Code', 'Example', 'Commodity Code', 'Commodity Title', 'Hot Technology']
  - `Knowledge.txt`: 57618 rows, columns: ['O*NET-SOC Code', 'Element ID', 'Element Name', 'Scale ID', 'Data Value']

### nonameee12233/job-resume-matching
- **Source URL**: https://huggingface.co/datasets/nonameee12233/job-resume-matching
- **License**: MIT
- **Intended Use**: Bipartite graph matching of resumes to job postings
- **SkillBridge AI Features Powered**: Feature 6 (Multi-Job Compatibility Engine), Feature 18 (Gap Priority Optimizer)
- **Audit Status**: `PARTIAL`
- **Component Tables**:
  - `matches.csv`: 122560 rows, columns: ['candidate_id', 'job_id', 'final_score', 'raw_score', 'label_strength']

### Google Research MBPP (Mostly Basic Python Problems)
- **Source URL**: https://github.com/google-research/google-research/tree/master/mbpp
- **License**: Apache-2.0
- **Intended Use**: Verified Python programming challenges with unit test assertions for practical skill assessment
- **SkillBridge AI Features Powered**: Feature 1 (Assessment Bank), Feature 13 (Adaptive Learning), Feature 15 (Coding Skill Analyzer)
- **Audit Status**: `VALIDATED`

## Conclusion & Preprocessing Strategy
- Datasets are kept cleanly segregated by feature domain to prevent artificial synthesis or ungrounded data leakage.
- O*NET 28.0/29.0 provides the occupational and skills ground truth.
- MBPP provides unit-testable coding challenges with sandboxed execution.
- HuggingFace resume and job datasets provide NLP training, skill extraction vocabulary, and fit verification benchmarks.