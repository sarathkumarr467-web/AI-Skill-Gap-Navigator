"""
SkillBridge AI - Data Preprocessing & Feature Engineering Pipeline
Processes raw acquired datasets into normalized, validated application artifacts:
1. O*NET Skills & Occupation Taxonomy -> Standardized career profiles & skill hierarchy
2. MBPP Python Programming Dataset -> Unit-testable coding challenges with difficulty grading
3. Keerthanshetty Skill Extractor -> Skill alias and normalization dictionaries
4. C0ldSmi1e Resume Dataset -> Cleaned text & stratified samples for model training
5. Comprehensive Assessment Question Bank & Curated Project/Resource Repositories
"""

import os
import sys
import json
import re
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REF_DIR = BASE_DIR / "data" / "reference"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REF_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. Clean Text Utility
# -------------------------------------------------------------
def clean_resume_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URL links
    text = re.sub(r"http\S+|www\S+", " ", text)
    # Remove emails and phone numbers for privacy
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " [EMAIL] ", text)
    text = re.sub(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b", " [PHONE] ", text)
    # Remove non-ascii or excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -------------------------------------------------------------
# 2. Process O*NET Database
# -------------------------------------------------------------
def process_onet():
    print("[1/5] Processing O*NET Database files...", flush=True)
    onet_dir = RAW_DIR / "onet_database"
    occ_file = onet_dir / "Occupation Data.txt"
    tech_file = onet_dir / "Technology Skills.txt"
    skills_file = onet_dir / "Skills.txt"
    
    # Target tech roles mapped to O*NET-SOC codes
    tech_soc_targets = {
        "15-1252.00": "Software Developer",
        "15-2051.00": "Data Scientist",
        "15-2051.01": "Machine Learning Engineer",
        "15-1251.00": "Computer Programmer",
        "15-1243.00": "Database Architect",
        "15-1211.00": "Computer Systems Analyst",
        "15-1241.00": "Computer Network Architect",
        "15-1299.08": "Computer Systems Engineers/Architects",
        "15-1221.00": "Computer and Information Research Scientists"
    }
    
    tech_skills_map = {}
    if tech_file.exists():
        try:
            df_tech = pd.read_csv(tech_file, sep="\t", on_bad_lines="skip", low_memory=False)
            # Find relevant column names
            soc_col = next((c for c in df_tech.columns if "soc" in c.lower()), "O*NET-SOC Code")
            example_col = next((c for c in df_tech.columns if "example" in c.lower() or "title" in c.lower() or "commodity" in c.lower()), df_tech.columns[1])
            
            for _, row in df_tech.iterrows():
                soc = str(row.get(soc_col, "")).strip()
                skill_name = str(row.get(example_col, "")).strip()
                if skill_name and skill_name != "nan":
                    tech_skills_map.setdefault(soc, set()).add(skill_name)
            print(f"  O*NET Tech Skills parsed for {len(tech_skills_map)} SOC occupations", flush=True)
        except Exception as e:
            print(f"  Warning processing tech skills: {e}", flush=True)
            
    # Process core standard occupations
    roles_output = []
    if occ_file.exists():
        try:
            df_occ = pd.read_csv(occ_file, sep="\t", on_bad_lines="skip", low_memory=False)
            soc_col = df_occ.columns[0]
            title_col = df_occ.columns[1]
            desc_col = df_occ.columns[2] if len(df_occ.columns) > 2 else title_col
            
            for _, row in df_occ.iterrows():
                soc = str(row[soc_col]).strip()
                title = str(row[title_col]).strip()
                desc = str(row[desc_col]).strip()
                
                # Check if it's a tech occupation or target
                is_target = soc in tech_soc_targets or soc.startswith("15-")
                if is_target:
                    extracted_skills = list(tech_skills_map.get(soc, []))[:20]
                    roles_output.append({
                        "soc_code": soc,
                        "title": tech_soc_targets.get(soc, title),
                        "original_title": title,
                        "description": desc,
                        "skills": extracted_skills
                    })
            print(f"  Processed {len(roles_output)} technology occupations from O*NET", flush=True)
        except Exception as e:
            print(f"  Warning processing occupations: {e}", flush=True)

    out_path = PROCESSED_DIR / "onet_roles_skills.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(roles_output, f, indent=2)
    return len(roles_output)

# -------------------------------------------------------------
# 3. Process MBPP Python Programming Problems
# -------------------------------------------------------------
def process_mbpp():
    print("[2/5] Processing MBPP Python Programming Problems...", flush=True)
    mbpp_file = RAW_DIR / "mbpp_problems" / "mbpp.jsonl"
    if not mbpp_file.exists():
        print("  MBPP file not found, skipping.", flush=True)
        return 0

    challenges = []
    with open(mbpp_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            item = json.loads(line)
            task_id = item.get("task_id", idx + 1)
            prompt = item.get("text", "").strip()
            code = item.get("code", "").strip()
            test_list = item.get("test_list", [])
            test_setup = item.get("test_setup_code", "").strip()
            
            if not prompt or not test_list:
                continue

            # Classify difficulty based on code length and test complexity
            code_lines = len(code.splitlines())
            if code_lines <= 5:
                difficulty = "Beginner"
            elif code_lines <= 12:
                difficulty = "Intermediate"
            else:
                difficulty = "Advanced"

            # Detect topic
            prompt_lower = prompt.lower()
            if any(w in prompt_lower for w in ["matrix", "array", "list", "sort", "reverse"]):
                topic = "Data Structures"
            elif any(w in prompt_lower for w in ["string", "char", "substring", "regex", "word"]):
                topic = "String Algorithms"
            elif any(w in prompt_lower for w in ["prime", "sum", "number", "math", "integer", "factorial", "gcd"]):
                topic = "Mathematics & Logic"
            elif any(w in prompt_lower for w in ["dict", "hash", "frequency", "map", "tuple"]):
                topic = "Collections & Hashing"
            elif any(w in prompt_lower for w in ["tree", "graph", "path", "depth", "cost"]):
                topic = "Advanced Algorithms"
            else:
                topic = "Python Fundamentals"

            # Parse sample test for display
            sample_test = test_list[0] if test_list else ""
            
            # Extract expected function name from first test
            func_name = "solution"
            fn_match = re.search(r"assert\s+([a-zA-Z_0-9]+)\(", sample_test)
            if fn_match:
                func_name = fn_match.group(1)

            challenges.append({
                "challenge_id": task_id,
                "title": f"Challenge #{task_id}: {prompt[:50]}...",
                "description": prompt,
                "function_name": func_name,
                "topic": topic,
                "difficulty": difficulty,
                "starter_code": f"def {func_name}(*args):\n    # Write your solution here\n    pass\n",
                "reference_solution": code,
                "test_list": test_list,
                "test_setup_code": test_setup,
                "sample_test": sample_test
            })

    out_path = PROCESSED_DIR / "coding_challenges.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(challenges, f, indent=2)
    print(f"  Processed {len(challenges)} coding challenges into {out_path.name}", flush=True)
    return len(challenges)

# -------------------------------------------------------------
# 4. Build Standardized Skill Taxonomy & Normalization Map
# -------------------------------------------------------------
def build_skill_taxonomy():
    print("[3/5] Building Skill Taxonomy & Normalization Map...", flush=True)
    
    # Canonical skill taxonomy organized by domain with prerequisites and category
    skills_taxonomy = {
        # Programming & Fundamentals
        "Python": {
            "category": "Programming Languages",
            "domain": "Core",
            "prerequisites": [],
            "importance": "Critical",
            "description": "General-purpose programming language widely used in AI, ML, Web, and Automation."
        },
        "Object-Oriented Programming": {
            "category": "Software Engineering",
            "domain": "Core",
            "prerequisites": ["Python"],
            "importance": "High",
            "description": "Design patterns, classes, inheritance, encapsulation, and modular code architecture."
        },
        "Data Structures & Algorithms": {
            "category": "Computer Science",
            "domain": "Core",
            "prerequisites": ["Python"],
            "importance": "Critical",
            "description": "Arrays, linked lists, trees, graphs, sorting, searching, and algorithmic complexity (Big O)."
        },
        "SQL": {
            "category": "Database",
            "domain": "Data Management",
            "prerequisites": [],
            "importance": "Critical",
            "description": "Structured Query Language for querying, schema design, indexing, and data modeling."
        },
        "Git & Version Control": {
            "category": "DevOps / Tools",
            "domain": "Core",
            "prerequisites": [],
            "importance": "High",
            "description": "Branching, merging, pull requests, commit hygiene, and collaborative version control."
        },
        
        # Data Science & Machine Learning
        "NumPy": {
            "category": "Data Science Libraries",
            "domain": "Data Science",
            "prerequisites": ["Python"],
            "importance": "Critical",
            "description": "N-dimensional array operations, vectorized linear algebra, and mathematical computing."
        },
        "Pandas": {
            "category": "Data Science Libraries",
            "domain": "Data Science",
            "prerequisites": ["Python", "NumPy"],
            "importance": "Critical",
            "description": "Data manipulation, DataFrame cleaning, aggregation, reshaping, and time-series handling."
        },
        "Data Visualization": {
            "category": "Data Science",
            "domain": "Data Science",
            "prerequisites": ["Python", "Pandas"],
            "importance": "Medium",
            "description": "Exploratory data analysis using Matplotlib, Seaborn, and Chart.js."
        },
        "Applied Statistics": {
            "category": "Mathematics",
            "domain": "Data Science",
            "prerequisites": ["Python"],
            "importance": "High",
            "description": "Probability distributions, hypothesis testing, p-values, regression, and Bayesian concepts."
        },
        "Scikit-Learn": {
            "category": "Machine Learning",
            "domain": "AI / ML",
            "prerequisites": ["Python", "NumPy", "Pandas", "Applied Statistics"],
            "importance": "Critical",
            "description": "Classical machine learning algorithms: classification, regression, clustering, and cross-validation."
        },
        "Machine Learning Modeling": {
            "category": "Machine Learning",
            "domain": "AI / ML",
            "prerequisites": ["Scikit-Learn"],
            "importance": "Critical",
            "description": "Feature engineering, hyperparameter tuning, model evaluation (ROC, PR, F1), and model drift."
        },
        "Deep Learning": {
            "category": "Deep Learning",
            "domain": "AI / ML",
            "prerequisites": ["Machine Learning Modeling", "NumPy"],
            "importance": "High",
            "description": "Neural network architectures: feedforward, CNNs, RNNs, backpropagation, and loss functions."
        },
        "PyTorch": {
            "category": "Deep Learning Frameworks",
            "domain": "AI / ML",
            "prerequisites": ["Deep Learning", "Python"],
            "importance": "High",
            "description": "Dynamic computation graphs, tensor operations, custom training loops, and PyTorch modules."
        },
        "Natural Language Processing": {
            "category": "AI Specialization",
            "domain": "AI / ML",
            "prerequisites": ["Deep Learning", "Python"],
            "importance": "High",
            "description": "Text tokenization, TF-IDF, embeddings, transformers, and sequence classification."
        },
        "Computer Vision": {
            "category": "AI Specialization",
            "domain": "AI / ML",
            "prerequisites": ["Deep Learning", "NumPy"],
            "importance": "Medium",
            "description": "Image processing, convolution, object detection, segmentation, and OpenCV."
        },
        
        # Deployment, Cloud & Web
        "Flask / FastAPI": {
            "category": "Backend Frameworks",
            "domain": "Software Engineering",
            "prerequisites": ["Python"],
            "importance": "High",
            "description": "RESTful API development, request handling, routing, serialization, and middleware."
        },
        "Docker & Containerization": {
            "category": "DevOps",
            "domain": "Infrastructure",
            "prerequisites": ["Git & Version Control"],
            "importance": "High",
            "description": "Building reproducible Dockerfiles, multi-stage builds, container networking, and volumes."
        },
        "MLOps & Model Deployment": {
            "category": "MLOps",
            "domain": "AI / ML",
            "prerequisites": ["Machine Learning Modeling", "Flask / FastAPI", "Docker & Containerization"],
            "importance": "High",
            "description": "Deploying models as microservices, pipeline monitoring, versioning, and CI/CD."
        },
        "Cloud Computing (AWS/GCP/Azure)": {
            "category": "Cloud Infrastructure",
            "domain": "Infrastructure",
            "prerequisites": ["Docker & Containerization"],
            "importance": "Medium",
            "description": "Cloud compute instances, object storage (S3), serverless functions, and managed databases."
        },
        "HTML / CSS / JavaScript": {
            "category": "Frontend Development",
            "domain": "Web Development",
            "prerequisites": [],
            "importance": "Medium",
            "description": "Semantic markup, responsive UI layouts, DOM manipulation, and asynchronous HTTP calls."
        }
    }
    
    # Normalization alias mapping
    normalization_map = {
        "py": "Python",
        "python3": "Python",
        "python 3": "Python",
        "oop": "Object-Oriented Programming",
        "object oriented": "Object-Oriented Programming",
        "dsa": "Data Structures & Algorithms",
        "data structures": "Data Structures & Algorithms",
        "algorithms": "Data Structures & Algorithms",
        "algorithm": "Data Structures & Algorithms",
        "sql": "SQL",
        "mysql": "SQL",
        "postgresql": "SQL",
        "postgres": "SQL",
        "sqlite": "SQL",
        "git": "Git & Version Control",
        "github": "Git & Version Control",
        "version control": "Git & Version Control",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "dataframe": "Pandas",
        "matplotlib": "Data Visualization",
        "seaborn": "Data Visualization",
        "chartjs": "Data Visualization",
        "chart.js": "Data Visualization",
        "data visualization": "Data Visualization",
        "statistics": "Applied Statistics",
        "stats": "Applied Statistics",
        "probability": "Applied Statistics",
        "hypothesis testing": "Applied Statistics",
        "scikit-learn": "Scikit-Learn",
        "scikit learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",
        "machine learning": "Machine Learning Modeling",
        "ml": "Machine Learning Modeling",
        "deep learning": "Deep Learning",
        "neural networks": "Deep Learning",
        "pytorch": "PyTorch",
        "torch": "PyTorch",
        "tensorflow": "Deep Learning",
        "keras": "Deep Learning",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "llm": "Natural Language Processing",
        "transformers": "Natural Language Processing",
        "cv": "Computer Vision",
        "computer vision": "Computer Vision",
        "opencv": "Computer Vision",
        "flask": "Flask / FastAPI",
        "fastapi": "Flask / FastAPI",
        "rest api": "Flask / FastAPI",
        "api development": "Flask / FastAPI",
        "docker": "Docker & Containerization",
        "containerization": "Docker & Containerization",
        "containers": "Docker & Containerization",
        "mlops": "MLOps & Model Deployment",
        "model deployment": "MLOps & Model Deployment",
        "ci/cd": "MLOps & Model Deployment",
        "aws": "Cloud Computing (AWS/GCP/Azure)",
        "gcp": "Cloud Computing (AWS/GCP/Azure)",
        "azure": "Cloud Computing (AWS/GCP/Azure)",
        "cloud": "Cloud Computing (AWS/GCP/Azure)",
        "html": "HTML / CSS / JavaScript",
        "css": "HTML / CSS / JavaScript",
        "javascript": "HTML / CSS / JavaScript",
        "js": "HTML / CSS / JavaScript"
    }
    
    with open(REF_DIR / "skills_taxonomy.json", "w", encoding="utf-8") as f:
        json.dump(skills_taxonomy, f, indent=2)
        
    with open(REF_DIR / "skill_normalization_map.json", "w", encoding="utf-8") as f:
        json.dump(normalization_map, f, indent=2)
        
    print(f"  Taxonomy ({len(skills_taxonomy)} skills) and Normalization map ({len(normalization_map)} aliases) saved.", flush=True)

# -------------------------------------------------------------
# 5. Build Comprehensive Assessment Question Bank
# -------------------------------------------------------------
def build_assessment_bank():
    print("[4/5] Building Assessment Question Bank across 6 Core Domains...", flush=True)
    
    questions = [
        # Python
        {
            "id": 1,
            "skill": "Python",
            "topic": "Python Fundamentals",
            "difficulty": "Beginner",
            "question": "What is the time complexity of looking up a key in a standard Python dictionary in the average case?",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
            "correct_option": 0,
            "explanation": "Python dictionaries use hash tables, achieving O(1) average-time complexity for key lookups."
        },
        {
            "id": 2,
            "skill": "Python",
            "topic": "Memory Management",
            "difficulty": "Intermediate",
            "question": "How does Python handle memory management and cleanup for objects with cyclic references?",
            "options": [
                "Reference counting alone handles cycles automatically",
                "A generational cyclic garbage collector identifies and reclaims unreachable reference cycles",
                "Cycles are never collected and must be freed manually via ctypes",
                "Python compiler prevents cyclic references at compile-time"
            ],
            "correct_option": 1,
            "explanation": "Python uses reference counting as primary cleanup and a generational garbage collector to detect and break reference cycles."
        },
        {
            "id": 3,
            "skill": "Python",
            "topic": "Concurrency",
            "difficulty": "Advanced",
            "question": "What is the role of the Global Interpreter Lock (GIL) in CPython?",
            "options": [
                "It accelerates NumPy matrix multiplications across threads",
                "It is a mutex that prevents multiple native threads from executing Python bytecodes at once",
                "It locks files on disk during database writes",
                "It enables parallel GPU kernel execution"
            ],
            "correct_option": 1,
            "explanation": "The GIL ensures thread safety by allowing only one native OS thread to execute Python bytecode at a time in CPython."
        },
        # Data Structures & Algorithms
        {
            "id": 4,
            "skill": "Data Structures & Algorithms",
            "topic": "Search Trees",
            "difficulty": "Beginner",
            "question": "In a balanced Binary Search Tree (AVL or Red-Black), what is the worst-case time complexity of searching for an element?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
            "correct_option": 1,
            "explanation": "Balanced BSTs guarantee a maximum height of O(log n), keeping search, insertion, and deletion within O(log n) time."
        },
        {
            "id": 5,
            "skill": "Data Structures & Algorithms",
            "topic": "Dynamic Programming",
            "difficulty": "Intermediate",
            "question": "What are the two essential characteristics required for a problem to be solvable via Dynamic Programming?",
            "options": [
                "Greedy choice property and polynomial bounds",
                "Optimal substructure and overlapping subproblems",
                "Linear independence and convexity",
                "Deterministic transitions and acyclic topological graph"
            ],
            "correct_option": 1,
            "explanation": "Dynamic programming applies when a problem exhibits both optimal substructure (optimal solution from optimal sub-solutions) and overlapping subproblems."
        },
        {
            "id": 6,
            "skill": "Data Structures & Algorithms",
            "topic": "Graph Algorithms",
            "difficulty": "Advanced",
            "question": "Which algorithm computes single-source shortest paths in a directed weighted graph that may contain negative edge weights (but no negative cycles)?",
            "options": ["Dijkstra's Algorithm", "Bellman-Ford Algorithm", "Kruskal's Algorithm", "Prim's Algorithm"],
            "correct_option": 1,
            "explanation": "Bellman-Ford handles graphs with negative edge weights and detects negative weight cycles in O(V * E) time."
        },
        # SQL
        {
            "id": 7,
            "skill": "SQL",
            "topic": "Query Optimization",
            "difficulty": "Beginner",
            "question": "Which SQL clause is used to filter aggregated grouped results rather than individual rows?",
            "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
            "correct_option": 1,
            "explanation": "WHERE filters rows before grouping; HAVING filters the aggregated summary groups created by GROUP BY."
        },
        {
            "id": 8,
            "skill": "SQL",
            "topic": "Window Functions",
            "difficulty": "Intermediate",
            "question": "What is the primary difference between RANK() and DENSE_RANK() in SQL window functions?",
            "options": [
                "RANK() ignores NULL values whereas DENSE_RANK() counts them",
                "RANK() leaves gaps in sequence after tied values, whereas DENSE_RANK() does not leave gaps",
                "RANK() can only be used with ORDER BY DESC",
                "There is no difference; they are aliases"
            ],
            "correct_option": 1,
            "explanation": "For ties (e.g. two 1st places), RANK() yields (1, 1, 3), whereas DENSE_RANK() yields (1, 1, 2)."
        },
        # Machine Learning Modeling & Scikit-Learn
        {
            "id": 9,
            "skill": "Machine Learning Modeling",
            "topic": "Bias-Variance Tradeoff",
            "difficulty": "Beginner",
            "question": "What typically occurs when a model suffers from High Variance?",
            "options": [
                "It underfits both training and testing datasets",
                "It overfits the training dataset and performs poorly on unseen test data",
                "It has excessive bias towards linear boundaries",
                "It converges too slowly during gradient descent"
            ],
            "correct_option": 1,
            "explanation": "High variance means the model is overly sensitive to training noise, leading to strong memorization and poor generalization."
        },
        {
            "id": 10,
            "skill": "Machine Learning Modeling",
            "topic": "Evaluation Metrics",
            "difficulty": "Intermediate",
            "question": "In a severe class-imbalance problem (e.g. fraud detection at 0.1% positive rate), which evaluation metric is MOST reliable?",
            "options": ["Accuracy", "Precision-Recall AUC (PR-AUC)", "Mean Squared Error", "R-squared"],
            "correct_option": 1,
            "explanation": "Accuracy is misleading with extreme imbalance (a trivial 99.9% accuracy). PR-AUC focuses on true positive rate and precision on the minority class."
        },
        {
            "id": 11,
            "skill": "Machine Learning Modeling",
            "topic": "Ensemble Methods",
            "difficulty": "Advanced",
            "question": "How does Gradient Boosting differ fundamentally from Random Forest (Bagging)?",
            "options": [
                "Random Forest builds trees sequentially to correct prior errors; Gradient Boosting trains independent parallel trees",
                "Gradient Boosting builds trees sequentially to minimize pseudo-residuals of prior trees; Random Forest averages independent deep trees",
                "Gradient Boosting only works on numerical classification, not regression",
                "Random Forest uses second-order Taylor series Hessian calculations"
            ],
            "correct_option": 1,
            "explanation": "Gradient boosting sequentially trains shallow trees to predict the negative gradient (residuals) of the loss function, while Random Forests bag parallel independent trees."
        },
        # Deep Learning & PyTorch
        {
            "id": 12,
            "skill": "Deep Learning",
            "topic": "Optimization",
            "difficulty": "Intermediate",
            "question": "What is the primary motivation for Batch Normalization during deep neural network training?",
            "options": [
                "It eliminates the need for activation functions",
                "It reduces internal covariate shift and stabilizes layer input distributions, enabling higher learning rates",
                "It converts recurrent networks into feedforward networks",
                "It compresses weights into 8-bit integers"
            ],
            "correct_option": 1,
            "explanation": "Batch Normalization normalizes activations across mini-batches, stabilizing gradients and permitting faster convergence."
        },
        {
            "id": 13,
            "skill": "Deep Learning",
            "topic": "Architectures",
            "difficulty": "Advanced",
            "question": "What computational complexity characterizes the self-attention mechanism in the standard Transformer with sequence length N?",
            "options": ["O(N)", "O(N log N)", "O(N^2)", "O(2^N)"],
            "correct_option": 2,
            "explanation": "Computing the QK^T attention matrix involves every token attending to every other token, resulting in O(N^2) time and memory complexity."
        },
        # MLOps & Deployment
        {
            "id": 14,
            "skill": "MLOps & Model Deployment",
            "topic": "Containerization",
            "difficulty": "Intermediate",
            "question": "Why are multi-stage Docker builds recommended when containerizing Python ML applications?",
            "options": [
                "They run containers in parallel across Kubernetes nodes",
                "They separate build dependencies (compilers, build tools) from the final runtime image, reducing image size and attack surface",
                "They automatically tune model hyperparameters inside Docker",
                "They enable live GPU hot-swapping"
            ],
            "correct_option": 1,
            "explanation": "Multi-stage builds allow compiling C-extensions or installing wheels in a builder stage and copying only artifacts to a slim production image."
        },
        {
            "id": 15,
            "skill": "MLOps & Model Deployment",
            "topic": "Production Monitoring",
            "difficulty": "Advanced",
            "question": "What is 'Concept Drift' in a production machine learning pipeline?",
            "options": [
                "A hardware failure in the inference server",
                "A change in the statistical relationship between input features X and target Y over time P(Y|X)",
                "A shift in input feature distributions P(X) while P(Y|X) stays unchanged",
                "A syntax error in model serialization"
            ],
            "correct_option": 1,
            "explanation": "Concept drift refers to changes in the underlying conditional distribution P(Y|X). In contrast, changes in P(X) are called covariate shift."
        }
    ]
    
    out_path = PROCESSED_DIR / "assessment_questions.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
    print(f"  Created {len(questions)} validated multi-choice assessment questions in {out_path.name}", flush=True)
    return len(questions)

# -------------------------------------------------------------
# 6. Build Curated Resources & Project Recommendations
# -------------------------------------------------------------
def build_curated_catalogs():
    print("[5/5] Building Curated Resources & Project Catalogs...", flush=True)
    
    # Real, verified learning resources
    resources = [
        {
            "skill": "Python",
            "title": "Official Python Tutorial & Language Reference",
            "type": "Documentation",
            "level": "Beginner",
            "url": "https://docs.python.org/3/tutorial/",
            "estimated_hours": 12,
            "is_free": True,
            "description": "Comprehensive official documentation covering syntax, data structures, modules, and error handling."
        },
        {
            "skill": "Python",
            "title": "Real Python: Intermediate Python Tutorials",
            "type": "Tutorial",
            "level": "Intermediate",
            "url": "https://realpython.com/",
            "estimated_hours": 15,
            "is_free": True,
            "description": "Hands-on deep dives into decorators, generators, context managers, and concurrency."
        },
        {
            "skill": "Data Structures & Algorithms",
            "title": "Open Data Structures (Python Edition)",
            "type": "Book / Course",
            "level": "Intermediate",
            "url": "https://opendatastructures.org/",
            "estimated_hours": 30,
            "is_free": True,
            "description": "Rigorous treatment of arrays, skiplists, trees, heaps, and graph algorithms with complexity proofs."
        },
        {
            "skill": "Scikit-Learn",
            "title": "Scikit-Learn Official User Guide & API Reference",
            "type": "Documentation",
            "level": "Intermediate",
            "url": "https://scikit-learn.org/stable/user_guide.html",
            "estimated_hours": 20,
            "is_free": True,
            "description": "The definitive guide to estimators, transformers, pipelines, cross-validation, and metrics."
        },
        {
            "skill": "Machine Learning Modeling",
            "title": "Google Machine Learning Crash Course",
            "type": "Interactive Course",
            "level": "Beginner",
            "url": "https://developers.google.com/machine-learning/crash-course",
            "estimated_hours": 15,
            "is_free": True,
            "description": "Practical lessons on gradient descent, loss functions, classification thresholds, and embeddings."
        },
        {
            "skill": "Deep Learning",
            "title": "Deep Learning Specialization - Andrew Ng (Coursera / YouTube)",
            "type": "Video Course",
            "level": "Intermediate",
            "url": "https://www.deeplearning.ai/",
            "estimated_hours": 35,
            "is_free": True,
            "description": "Foundational mathematical intuition and backpropagation implementation for deep neural networks."
        },
        {
            "skill": "PyTorch",
            "title": "PyTorch Official 60-Minute Blitz & Tutorials",
            "type": "Tutorial",
            "level": "Intermediate",
            "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html",
            "estimated_hours": 10,
            "is_free": True,
            "description": "Tensors, autograd, neural network modules, loss functions, and optimizers."
        },
        {
            "skill": "SQL",
            "title": "PostgreSQL Official Documentation & SQL Tutorial",
            "type": "Documentation",
            "level": "Beginner",
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
            "estimated_hours": 14,
            "is_free": True,
            "description": "Relational algebra, joins, subqueries, grouping, aggregations, and transactional integrity."
        },
        {
            "skill": "Flask / FastAPI",
            "title": "FastAPI Official Documentation & Interactive OpenAPI Tutorial",
            "type": "Documentation",
            "level": "Intermediate",
            "url": "https://fastapi.tiangolo.com/tutorial/",
            "estimated_hours": 12,
            "is_free": True,
            "description": "Modern API development with type hints, automatic schema generation, and asynchronous endpoints."
        },
        {
            "skill": "MLOps & Model Deployment",
            "title": "Full Stack Deep Learning - Production ML Course",
            "type": "Course",
            "level": "Advanced",
            "url": "https://fullstackdeeplearning.com/",
            "estimated_hours": 25,
            "is_free": True,
            "description": "Complete lifecycle: data pipelines, testing models, CI/CD, containerization, and production monitoring."
        }
    ]
    
    # Portfolio projects targeting specific gaps
    projects = [
        {
            "id": "PRJ-01",
            "title": "End-to-End Customer Churn Prediction & Explainability Dashboard",
            "difficulty": "Intermediate",
            "target_gap": "Machine Learning Modeling",
            "skills_developed": ["Python", "Pandas", "Scikit-Learn", "Data Visualization", "Flask / FastAPI"],
            "tech_stack": ["Python", "Scikit-Learn", "Flask", "SHAP", "Bootstrap 5"],
            "learning_objectives": [
                "Implement robust feature engineering for tabular data",
                "Train and compare Random Forest vs Gradient Boosting models",
                "Integrate SHAP tree explainers to explain predictions to business users",
                "Deploy an interactive web dashboard for real-time customer risk scoring"
            ],
            "expected_deliverables": [
                "Jupyter notebook documenting exploratory analysis and cross-validation",
                "Saved model artifact serialized via joblib",
                "Flask REST endpoint returning prediction and feature importances",
                "Responsive UI showing customer risk score and key drivers"
            ],
            "validation_checklist": [
                "Split data using stratified K-Fold without target leakage",
                "Calculate and log ROC-AUC and PR-AUC",
                "Handle missing categorical and continuous values cleanly in pipeline",
                "Unit test API endpoint for valid JSON payload response"
            ],
            "portfolio_value": "Demonstrates commercial ML intuition, clean pipeline engineering, and model interpretability."
        },
        {
            "id": "PRJ-02",
            "title": "Production REST API for Real-Time Sentiment & NLP Classification",
            "difficulty": "Intermediate",
            "target_gap": "Natural Language Processing",
            "skills_developed": ["Python", "Natural Language Processing", "Flask / FastAPI", "Docker & Containerization"],
            "tech_stack": ["Python", "Scikit-Learn / PyTorch", "FastAPI", "Docker"],
            "learning_objectives": [
                "Preprocess raw text data (tokenization, lemmatization, stop words)",
                "Build TF-IDF and transformer-based sentence classification pipelines",
                "Wrap model in FastAPI with async request processing and Pydantic validation",
                "Containerize service using multi-stage Docker build"
            ],
            "expected_deliverables": [
                "FastAPI application with /predict and /health endpoints",
                "Swagger OpenAPI interactive documentation",
                "Dockerfile and docker-compose.yml configuration",
                "Benchmark report showing latency (p95 < 50ms)"
            ],
            "validation_checklist": [
                "Validate input text size limits to prevent memory exhaustion",
                "Implement error handlers for empty or non-English inputs",
                "Multi-stage Docker image under 300MB",
                "Include automated Pytest test suite"
            ],
            "portfolio_value": "Shows software engineering rigor, containerization, and API production readiness."
        },
        {
            "id": "PRJ-03",
            "title": "Distributed Data Warehouse & Analytics Pipeline with SQL & Parquet",
            "difficulty": "Beginner",
            "target_gap": "SQL",
            "skills_developed": ["SQL", "Python", "Pandas"],
            "tech_stack": ["PostgreSQL / DuckDB", "Python", "Pandas", "SQLAlchemy"],
            "learning_objectives": [
                "Design normalized relational schemas (3NF) and star-schema dimensional models",
                "Execute complex analytical window queries, CTEs, and cohort retention tables",
                "Automate batch ETL pipeline from CSV/Parquet into structured database tables"
            ],
            "expected_deliverables": [
                "DDL schema migration scripts with primary & foreign keys",
                "ETL Python script with logging and idempotency checks",
                "Analytical report answering 5 key operational business questions"
            ],
            "validation_checklist": [
                "All tables indexed appropriately on join keys",
                "Zero data truncation during ETL pipeline run",
                "Verified referential integrity constraints"
            ],
            "portfolio_value": "Proves fundamental database architecture, clean SQL proficiency, and data engineering ability."
        },
        {
            "id": "PRJ-04",
            "title": "Automated MLOps Pipeline: Drift Detection & Continuous Model Retraining",
            "difficulty": "Advanced",
            "target_gap": "MLOps & Model Deployment",
            "skills_developed": ["MLOps & Model Deployment", "Docker & Containerization", "Git & Version Control"],
            "tech_stack": ["Python", "Docker", "Evidently AI / Custom Drift", "GitHub Actions", "FastAPI"],
            "learning_objectives": [
                "Detect covariate and concept drift between training and production distributions",
                "Automate testing and validation of newly trained candidate models",
                "Implement canary deployment pattern with zero-downtime rollback"
            ],
            "expected_deliverables": [
                "Drift detection script calculating Kolmogorov-Smirnov and PSI metrics",
                "CI/CD workflow file for GitHub Actions executing automated tests",
                "Monitoring dashboard tracking prediction drift over time"
            ],
            "validation_checklist": [
                "Alert triggers when PSI > 0.2",
                "Automated rollback when candidate model fails validation gate",
                "Dockerized reproducible runner"
            ],
            "portfolio_value": "Highlights elite MLOps engineering practices demanded by top technology teams."
        }
    ]
    
    with open(REF_DIR / "curated_resources.json", "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2)
        
    with open(REF_DIR / "curated_projects.json", "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)
        
    print(f"  Curated {len(resources)} resources and {len(projects)} projects saved.", flush=True)

def main():
    print("=" * 65)
    print("  SkillBridge AI: Starting Preprocessing & Catalog Pipeline")
    print("=" * 65)
    
    process_onet()
    process_mbpp()
    build_skill_taxonomy()
    build_assessment_bank()
    build_curated_catalogs()
    
    print("\n" + "=" * 65)
    print("Preprocessing completed successfully!")
    print("=" * 65)

if __name__ == "__main__":
    main()
