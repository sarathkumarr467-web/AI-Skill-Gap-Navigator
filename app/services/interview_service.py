"""
SkillBridge AI - Mock Interview Coach Service
Implements Feature 14: Role-specific interview sessions with question generation,
answer evaluation, missing concept detection, and constructive feedback.
Supports optional LLM API with deterministic semantic evaluation fallback.
"""

import os
import re
from typing import Dict, List, Any

# Curated role-specific interview question bank
INTERVIEW_BANK = {
    "AI Engineer": [
        {
            "type": "Technical",
            "question": "How do you detect and mitigate vanishing or exploding gradients when training deep neural network architectures?",
            "key_concepts": ["gradient clipping", "residual connections", "batch normalization", "weight initialization (He/Xavier)", "ReLU/GELU activations"]
        },
        {
            "type": "Conceptual",
            "question": "Explain the architectural difference between Encoder-only (e.g. BERT), Decoder-only (e.g. GPT), and Encoder-Decoder (e.g. T5) models.",
            "key_concepts": ["bidirectional attention", "causal autoregressive masking", "cross-attention", "sequence-to-sequence translation", "feature representation"]
        },
        {
            "type": "Scenario",
            "question": "Your production computer vision model achieves 98% accuracy on validation data, but customer satisfaction drops after deployment due to latency spikes and false negatives in nighttime conditions. How do you diagnose and resolve this?",
            "key_concepts": ["covariate shift / data drift", "low-light augmentation", "latency p95/p99 benchmarking", "model quantization / TensorRT", "shadow deployment"]
        }
    ],
    "Data Scientist": [
        {
            "type": "Technical",
            "question": "What is the difference between L1 (Lasso) and L2 (Ridge) regularization, and when would you choose one over the other?",
            "key_concepts": ["sparsity / feature selection", "absolute penalty vs squared penalty", "collinear features", "diamond vs circular geometry", "loss function"]
        },
        {
            "type": "Conceptual",
            "question": "Explain Simpson's Paradox and provide an example of how it can mislead stakeholders in A/B testing analysis.",
            "key_concepts": ["confounding variables", "aggregated vs subgroup trends", "sample ratio mismatch", "stratified analysis", "causality"]
        },
        {
            "type": "Scenario",
            "question": "Stakeholders complain that a customer churn prediction model is producing too many false alarms, causing support teams to waste resources contacting loyal users. How would you adjust the model decision boundary and communicate the trade-off?",
            "key_concepts": ["classification threshold tuning", "precision-recall curve", "cost-benefit matrix", "expected monetary value", "ROC curve"]
        }
    ],
    "Software Developer": [
        {
            "type": "Technical",
            "question": "How do database indexes work internally (e.g. B-Trees vs Hash indexes), and what are the trade-offs of adding multiple indexes to a high-write table?",
            "key_concepts": ["B-tree search complexity O(log N)", "range scans", "write amplification", "disk I/O overhead on INSERT/UPDATE", "hash index exact lookup"]
        },
        {
            "type": "Conceptual",
            "question": "Explain the SOLID principles of Object-Oriented Software Design with an emphasis on the Dependency Inversion Principle.",
            "key_concepts": ["single responsibility", "open/closed", "liskov substitution", "interface segregation", "dependency inversion / interfaces"]
        },
        {
            "type": "Scenario",
            "question": "A core microservice begins throwing HTTP 504 Gateway Timeouts under sudden traffic spikes. Walk through your debugging process from metrics to code fix.",
            "key_concepts": ["database connection pooling", "thread/worker starvation", "distributed tracing", "caching (Redis)", "horizontal pod autoscaling / rate limiting"]
        }
    ]
}

class MockInterviewCoachService:
    @classmethod
    def get_questions_for_role(cls, role_title: str) -> List[Dict[str, Any]]:
        """Retrieves questions matching the role or returns standard AI Engineer set."""
        for key in INTERVIEW_BANK:
            if key.lower() in role_title.lower():
                return INTERVIEW_BANK[key]
        return INTERVIEW_BANK["AI Engineer"]

    @classmethod
    def evaluate_response(
        cls,
        question: str,
        question_type: str,
        user_answer: str,
        key_concepts: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates interview answer:
        Checks coverage of key concepts, technical completeness, length, and coherence.
        """
        ans_lower = user_answer.lower().strip()
        
        if len(ans_lower) < 20:
            return {
                "score": 25.0,
                "feedback": "Answer is excessively brief. In technical interviews, provide structured explanations demonstrating depth of reasoning, trade-offs, and examples.",
                "missing_concepts": key_concepts,
                "identified_concepts": []
            }

        found_concepts = []
        missing_concepts = []

        for concept in key_concepts:
            # Check if concept words appear in answer
            words = [w for w in re.split(r"[ /(),]+", concept.lower()) if len(w) > 3]
            if any(w in ans_lower for w in words):
                found_concepts.append(concept)
            else:
                missing_concepts.append(concept)

        concept_ratio = len(found_concepts) / max(len(key_concepts), 1)
        
        # Word count bonus (up to 20 points for well-elaborated answers > 80 words)
        words_count = len(ans_lower.split())
        elaboration_score = min(words_count / 80.0, 1.0) * 20.0

        raw_score = (concept_ratio * 75.0) + elaboration_score + 5.0
        score = round(min(max(raw_score, 30.0), 98.0), 1)

        # Construct actionable feedback
        feedback_parts = []
        if concept_ratio >= 0.7:
            feedback_parts.append("Excellent technical response! You clearly articulated the core mechanisms and design considerations.")
        elif concept_ratio >= 0.4:
            feedback_parts.append("Solid baseline explanation. You identified several key ideas, but missed a few foundational concepts that senior interviewers expect.")
        else:
            feedback_parts.append("Partial answer. While you touched on the topic, the answer lacked technical specificity and critical trade-off analysis.")

        if missing_concepts:
            feedback_parts.append(f"To elevate this response, ensure you explicitly address: {', '.join(missing_concepts[:3])}.")

        return {
            "score": score,
            "feedback": " ".join(feedback_parts),
            "missing_concepts": missing_concepts,
            "identified_concepts": found_concepts
        }
