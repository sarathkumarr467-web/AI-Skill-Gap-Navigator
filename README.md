# SkillBridge AI — Intelligent Skill Gap Analysis & Career Intelligence Platform

<p align="center">

**Discover Your Gaps. Master Your Skills. Prove Your Potential.**

An AI-powered career intelligence and skill development platform that transforms skill assessments, resume analysis, coding practice, and career requirements into a personalized, evidence-driven learning journey.

**Team NEXORA** | **Presented by SARATHKUMAR R**

</p>

---

## 1. Project Overview

### What is SkillBridge AI?

SkillBridge AI is an intelligent, end-to-end career development platform designed to help engineering students and aspiring technology professionals identify their skill gaps, evaluate their technical capabilities, understand industry expectations, and build a structured path toward career readiness.

Traditional career preparation often involves disconnected activities: learning programming languages, attending assessments, solving coding problems, preparing resumes, and applying for jobs.

SkillBridge AI brings these activities together into one integrated intelligence platform.

Instead of relying entirely on self-reported skills, the system combines assessment results, coding performance, resume evidence, and portfolio verification to develop a more meaningful picture of a candidate's capabilities.

### Our Vision

To transform career preparation from guesswork into a measurable, evidence-based, continuously improving process.

### Core Philosophy

**A skill should not simply be claimed. It should be demonstrated, evaluated, and continuously improved.**

---

## 2. The SkillBridge Intelligence Workflow

SkillBridge AI operates through a continuous eight-stage development cycle.

```text
       ASSESS
          |
          v
       ANALYSE
          |
          v
       IDENTIFY
          |
          v
      PRIORITISE
          |
          v
        LEARN
          |
          v
       PRACTISE
          |
          v
      REASSESS
          |
          v
       IMPROVE
          |
          +----------> Continuous Learning
```

| Stage | Intelligence Process |
|---|---|
| Assess | Evaluate technical knowledge through domain-based assessments. |
| Analyse | Examine skills, resume information, coding performance, and evidence. |
| Identify | Detect missing competencies against career-role requirements. |
| Prioritise | Rank skill gaps based on importance, deficit, and dependencies. |
| Learn | Generate structured learning roadmaps and recommend resources. |
| Practise | Improve through coding challenges and mock interviews. |
| Reassess | Evaluate updated competencies using new evidence. |
| Improve | Track progress and continuously update career readiness. |

The outcome is not just a skill-gap report. It is an integrated career development process.

---

## 3. Twenty Core Feature Groups

SkillBridge AI incorporates 20 interconnected feature groups.

### A. Skill Intelligence & Assessment

**01. AI-Powered Skill Assessment**

- Six domain-based assessment suites.
- Multi-topic technical evaluation.
- Adaptive scoring mechanisms.
- Database-backed assessment history.

**02. Evidence-Based Skill Verification**

- Distinguishes self-reported skills from verified capabilities.
- Uses assessment results, coding performance, and portfolio evidence.
- Maintains user-specific skill evidence.

**03. Skill Dependency Intelligence**

- Represents prerequisite relationships using Directed Acyclic Graphs (DAGs).
- Implements three-color DFS cycle detection.
- Uses topological sorting to identify valid learning sequences.

**04. Personalized Skill Gap Detection**

- Compares candidate competencies with O*NET career-role benchmarks.
- Identifies missing and underdeveloped skills.
- Calculates skill deficit metrics.

### B. Career & Job Intelligence

**05. Smart Job Description Analyzer**

- Extracts technical skills from job descriptions.
- Separates required and preferred qualifications.
- Identifies experience-level requirements.
- Uses NLP-based skill recognition and normalization.

**06. Multi-Job Compatibility Engine**

Evaluates candidate compatibility across five career paths:

- AI Engineer
- Data Scientist
- Machine Learning Engineer
- Software Developer
- Data Analyst

**07. Explainable Job-Readiness Score**

A transparent four-factor scoring model:

| Evaluation Factor | Weight |
|---|---:|
| Skill Coverage | 40% |
| Assessment Performance | 30% |
| Coding Performance | 20% |
| Portfolio Evidence | 10% |

The score provides a diagnostic estimate of preparation, not a guarantee of employment.

**08. Career Path Simulator**

- Evaluates career transitions.
- Identifies transferable competencies.
- Estimates study hours required for target roles.

**09. Skill Demand Intelligence**

- Analyses skill frequency from O*NET occupational data.
- Helps users understand career-role skill requirements.
- Supports informed learning priorities.

### C. Personalized Learning Intelligence

**10. AI Learning Roadmap Generator**

- Generates personalized weekly milestones.
- Considers available weekly study hours.
- Respects prerequisite skill dependencies.
- Organizes learning into structured sequences.

**11. Smart Resource Recommendation**

- Recommends curated technical documentation.
- Provides learning resources based on skill and proficiency level.
- Supports focused learning.

**12. AI Project Recommendation Engine**

- Recommends portfolio-building projects.
- Connects project recommendations with identified skill gaps.
- Includes recruiter-oriented validation checklists.

**13. Adaptive Learning System**

- Identifies weak assessment subtopics.
- Updates skill proficiency evidence.
- Uses new performance information to support continuous improvement.

### D. Practical Evaluation & Career Preparation

**14. AI Mock Interview Coach**

- Provides role-specific technical and scenario-based questions.
- Evaluates responses.
- Identifies important concepts covered in answers.

**15. Coding Skill Analyzer**

- Integrates Google Research MBPP programming problems.
- Supports Python coding practice.
- Includes AST-based static security screening.
- Executes code using an isolated subprocess runner with execution timeouts.

**16. Portfolio Evidence Analyzer**

Evaluates portfolio evidence through:

- GitHub repository analysis.
- Unit testing information.
- Docker configuration.
- Architecture documentation.

### E. Continuous Career Intelligence

**17. Skill Proof Portfolio (PDF Export)**

- Generates downloadable PDF skill reports.
- Uses ReportLab.
- Organizes verified skill evidence and performance information.

**18. Skill Gap Priority Optimizer**

Prioritizes missing competencies using:

- Skill criticality.
- Deficit magnitude.
- Prerequisite leverage.

**19. What-If Career Simulator**

- Simulates potential readiness improvements.
- Evaluates the effect of additional study hours.
- Provides interactive career-readiness projections.

**20. Continuous Skill Intelligence**

- Maintains longitudinal progress snapshots.
- Tracks readiness trends over time.
- Supports measurable skill development.

---

## 4. System Architecture

SkillBridge AI follows a modular Flask application architecture.

```text
                  USER INTERFACE
                        |
                        v
              HTML / CSS / JavaScript
                        |
                        v
                FLASK APPLICATION
                        |
             MODULAR BLUEPRINT ROUTES
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
  ASSESSMENT        CAREER & GAP       LEARNING
    ENGINE            ENGINE           ENGINE
       |                |                |
       +----------------+----------------+
                        |
                        v
                 SERVICE LAYER
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
   ML / NLP        SKILL INTELLIGENCE   PRACTICE
   SERVICES          SERVICES          SERVICES
       |                |                |
       +----------------+----------------+
                        |
                        v
                SQLALCHEMY ORM
                        |
                        v
                   SQLITE DB
                        |
                        v
             USER DATA & PROGRESS
```

### Architectural Principles

- Modular Flask Blueprints.
- Separation of routes, services, and models.
- SQLAlchemy-based database access.
- Reusable AI and business logic services.
- Persistent user-specific records.
- Configuration-based application environments.

---

## 5. AI, Machine Learning & Algorithms

SkillBridge AI combines practical machine learning, natural language processing, data analysis, and algorithmic intelligence.

### Machine Learning

- TF-IDF Vectorization.
- Regularized Logistic Regression.
- Joblib model serialization.
- Resume classification.
- Semantic skill matching.

### Natural Language Processing

- Resume text extraction.
- Job description parsing.
- Technical skill identification.
- Skill alias normalization.
- Required versus preferred qualification extraction.

### Core Algorithms

| Algorithm / Technique | Application |
|---|---|
| TF-IDF | Resume text feature extraction |
| Logistic Regression | Resume classification |
| DFS Three-Color Algorithm | Dependency cycle detection |
| Topological Sorting | Learning prerequisite ordering |
| Rule-based prioritization | Skill gap optimization |
| Weighted scoring | Job-readiness estimation |
| AST Analysis | Coding security screening |

---

## 6. Machine Learning Model & Actual Evaluation

### Resume Classification Model

The resume classification component uses a TF-IDF-based Logistic Regression model.

**Model:** TFIDF_LogisticRegression_Resume_Classifier

**Dataset:** C0ldSmi1e/resume-dataset

**Evaluation configuration:**

| Metric | Actual Value |
|---|---:|
| Training Samples | 2,257 |
| Testing Samples | 98 |
| Number of Classes | 23 |
| Training Time | 8.96 seconds |
| Accuracy | 54.08% |
| Weighted Precision | 95.06% |
| Weighted Recall | 54.08% |
| Weighted F1 Score | 68.23% |
| Macro F1 Score | 10.02% |

**Evaluation Interpretation**

The dataset contains 23 specialized professional categories with class imbalance.

The weighted precision is 95.06%, while the macro F1 score is 10.02%. This difference indicates that performance varies significantly across categories, particularly minority classes.

These are the recorded evaluation metrics, not projected or fabricated results.

Model artifacts and metrics are maintained in the `models/` directory.

---

## 7. Real Dataset Integration

SkillBridge AI incorporates external datasets to support its assessment, programming, and career intelligence components.

### Dataset Sources

**1. Official O*NET Database**

Used for occupational information and career-role skill benchmarks.

- Occupational information.
- Career skill requirements.
- Role-based skill comparisons.
- Skill demand intelligence.

**2. Google Research MBPP**

Used for Python programming practice and coding evaluation.

- Programming problems.
- Coding challenges.
- Practical programming exercises.

**3. Hugging Face Datasets**

Used for dataset-based NLP and resume-related processing.

- C0ldSmi1e/resume-dataset.
- med2425_job_fit dataset.

### Data Processing Pipeline

```text
EXTERNAL DATA SOURCES
         |
         v
    DATA DOWNLOAD
         |
         v
   DATA VALIDATION
         |
         v
   DATA PREPROCESSING
         |
         v
   DATA NORMALIZATION
         |
         v
   MODEL TRAINING /
   REFERENCE GENERATION
         |
         v
   APPLICATION INTEGRATION
```

Dataset licensing and usage conditions should be respected when redistributing data.

---

## 8. Technology Stack

| Layer | Technologies |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | Flask |
| Application Architecture | Flask Blueprints |
| Database | SQLite |
| ORM | Flask-SQLAlchemy |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| NLP | TF-IDF, Logistic Regression, Regex |
| Model Persistence | Joblib |
| Resume Processing | PyMuPDF, python-docx, PyPDF |
| PDF Generation | ReportLab |
| Frontend | HTML5, CSS3, JavaScript ES6 |
| UI Framework | Bootstrap 5 |
| Icons | Bootstrap Icons |
| Visualization | Chart.js 4.4 |
| Security Analysis | Python AST |
| Testing | Python unittest |

---

## 9. Project Directory Structure

```text
SkillBridge-AI/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── skill.py
│   │   ├── career.py
│   │   ├── assessment.py
│   │   ├── evidence.py
│   │   ├── roadmap.py
│   │   └── progress.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── assessment_routes.py
│   │   ├── gap_routes.py
│   │   ├── analyzer_routes.py
│   │   ├── learning_routes.py
│   │   └── practice_routes.py
│   │
│   ├── services/
│   │   ├── assessment_service.py
│   │   ├── skill_extractor.py
│   │   ├── dependency_service.py
│   │   ├── gap_service.py
│   │   ├── readiness_service.py
│   │   ├── compatibility_service.py
│   │   ├── career_simulator_service.py
│   │   ├── roadmap_service.py
│   │   ├── coding_sandbox_service.py
│   │   ├── interview_service.py
│   │   ├── portfolio_service.py
│   │   └── report_service.py
│   │
│   └── templates/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── reference/
│   └── README.md
│
├── models/
│   ├── resume_classifier.joblib
│   ├── semantic_skill_matcher.joblib
│   └── classifier_metrics.json
│
├── scripts/
│   ├── download_data.py
│   ├── validate_data.py
│   ├── preprocess_data.py
│   ├── train_models.py
│   └── initialize_db.py
│
├── tests/
│   └── test_skillbridge.py
│
└── reports/
    ├── data_validation_report.json
    └── data_validation_report.md
```

---

## 10. Installation & Local Setup

### Prerequisites

- Python 3.12
- Git
- VS Code or another Python-compatible IDE
- Windows PowerShell (for the commands below)

### Step 1: Clone the Repository

```bash
git clone https://github.com/sarathkumarr467-web/AI-Skill-Gap-Navigator.git
```

```bash
cd AI-Skill-Gap-Navigator
```

### Step 2: Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create your local `.env` file using `.env.example` as a reference.

Add the required configuration values supported by your application.

Never commit real secrets, passwords, or production credentials.

### Step 5: Prepare and Validate Datasets

```bash
python scripts/download_data.py
```

```bash
python scripts/preprocess_data.py
```

```bash
python scripts/validate_data.py
```

Dataset files excluded from GitHub must be downloaded locally before running features that depend on them.

### Step 6: Initialize the Database

```bash
python scripts/initialize_db.py
```

### Step 7: Start the Application

```bash
python app.py
```

Open your browser:

**http://localhost:5000**

Register an account or use the application's demo-login option if enabled.

---

## 11. Automated Testing

SkillBridge AI includes an automated testing suite using Python's unittest framework.

Run the tests:

```bash
python -m unittest tests.test_skillbridge
```

### Testing Areas

- Application factory and startup.
- Candidate registration and authentication.
- Session persistence and authorization isolation.
- NLP skill extraction and alias normalization.
- Job description qualification parsing.
- Skill dependency DAG cycle detection.
- Topological learning sequence generation.
- Explainable readiness scoring.
- Sandboxed code execution and AST security checks.
- Mock interview evaluation.
- Portfolio repository auditing.
- PDF skill proof generation.

Testing helps validate individual modules and their integration.

---

## 12. Responsible AI, Privacy & Security

SkillBridge AI incorporates several mechanisms intended to support responsible and secure application behaviour.

### AST-Based Code Screening

User-submitted Python code is inspected using an Abstract Syntax Tree visitor.

The implementation identifies restricted operations and blocked library imports, including:

- `open`
- `eval`
- `exec`
- `os`
- `sys`
- `subprocess`
- `socket`

Execution is performed using an isolated subprocess runner with a 3.5-second timeout.

**Note:** Static screening and subprocess isolation are protective measures, not a guarantee of complete sandbox security. Production deployment requires additional operating-system-level isolation and resource restrictions.

### Transparent Readiness Scoring

The readiness score uses documented factor weights:

- Skill Coverage: 40%.
- Assessment: 30%.
- Coding: 20%.
- Portfolio: 10%.

The score is a diagnostic estimate, not a hiring decision or employment guarantee.

### Privacy-Aware Resume Processing

The implementation includes:

- PII stripping before resume parsing.
- User-isolated document storage.
- Password hashing using Werkzeug PBKDF2/SHA-256.
- Restricted user-specific data access.

Users should be informed about how their resume information is processed and stored.

---

## 13. What Makes SkillBridge AI Different?

| Traditional Career Preparation | SkillBridge AI |
|---|---|
| Separate assessment platforms | Integrated skill assessment |
| Self-reported skills | Evidence-based verification |
| Manual skill gap identification | Automated gap analysis |
| Generic learning plans | Personalized learning roadmaps |
| Isolated coding practice | Integrated coding evaluation |
| Unstructured career exploration | Multi-job compatibility |
| Static progress tracking | Continuous skill intelligence |
| Unexplained readiness estimates | Transparent weighted scoring |

### Our Core Innovation

The central innovation is the integration of multiple career preparation activities into one evidence-driven feedback loop.

A candidate can assess their skills, understand deficiencies, prioritize improvements, learn missing competencies, practise technical problems, and reassess progress within the same platform.

This creates a connected approach to career development rather than a collection of independent tools.

---

## 14. Future Development Scope

Potential future enhancements include:

- Expanded occupational and industry datasets.
- Additional career-role compatibility models.
- More programming languages in coding practice.
- Advanced semantic skill matching.
- Expanded assessment domains.
- Enhanced learning analytics.
- More detailed portfolio verification.
- Production-grade deployment and security hardening.
- Integration with additional verified learning resources.

These are potential enhancements, not claims of already implemented functionality.

---

## 15. Project Information & Credits

| Field | Details |
|---|---|
| Project Name | SkillBridge AI |
| Full Title | Intelligent Skill Gap Analysis & Career Intelligence Platform |
| Team | NEXORA |
| Presented By | SARATHKUMAR R |
| Domain | Artificial Intelligence, Machine Learning, NLP |
| Backend | Python & Flask |
| Database | SQLite |
| Core Feature Groups | 20 |
| Project Type | AI-Powered Career Intelligence Platform |

### Project Tagline

**Discover Your Gaps. Master Your Skills. Prove Your Potential.**

---

## 16. Acknowledgements & Data Sources

We acknowledge the organizations and communities providing the datasets and technical resources used in this project:

- [O*NET Resource Center](https://www.onetcenter.org/)
- [Google Research – MBPP](https://github.com/google-research/google-research/tree/master/mbpp)
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [Scikit-learn](https://scikit-learn.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)

Dataset ownership, attribution, and licensing remain subject to their respective original terms.

---

<p align="center">

**SkillBridge AI | Team NEXORA**

*Turning Skill Gaps into Career Growth.*

**Discover. Analyse. Learn. Practise. Improve.**

</p>
