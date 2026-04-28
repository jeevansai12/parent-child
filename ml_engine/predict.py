"""
predict.py
──────────
Load the trained GradientBoosting model and run inference on a single set of
10 Likert-scale answers.

Returns:
    (score: float, category: str)
    score    → mapped to 1-3 range
    category → 'Weak' | 'Moderate' | 'Strong'
"""

import os
import numpy as np
import joblib

_MODEL = None  # lazily loaded

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model.pkl')

# Internal class indices → score mapping
_CLASS_SCORE = {0: 1.0, 1: 2.0, 2: 3.0}
_CLASS_LABEL = {0: 'Weak', 1: 'Moderate', 2: 'Strong'}


def _load_model():
    global _MODEL
    if _MODEL is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. "
                "Run 'python ml_engine/train_model.py' first."
            )
        _MODEL = joblib.load(MODEL_PATH)
    return _MODEL


def run_prediction(answers: list) -> tuple:
    """
    Args:
        answers: list of 10 integers (Likert 1-5), ordered pq1…pq10

    Returns:
        (score, category): e.g. (2.74, 'Strong')
    """
    if len(answers) != 10:
        raise ValueError(f"Expected 10 answers, got {len(answers)}")

    model = _load_model()
    X = np.array(answers, dtype=float).reshape(1, -1)

    pred_class = int(model.predict(X)[0])
    pred_proba = model.predict_proba(X)[0]  # shape (3,)

    # Score = weighted sum: class 0→1, 1→2, 2→3
    score = float(
        pred_proba[0] * 1.0 +
        pred_proba[1] * 2.0 +
        pred_proba[2] * 3.0
    )
    # Clamp to [1, 3]
    score = max(1.0, min(3.0, score))
    category = _CLASS_LABEL[pred_class]

    return round(score, 2), category
