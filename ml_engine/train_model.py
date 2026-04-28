"""
train_model.py
─────────────
Generates a synthetic dataset and trains a GradientBoostingClassifier to
predict communication quality (Weak / Moderate / Strong).

Run once before starting the server:
    python ml_engine/train_model.py
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# ── Path setup ──────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(script_dir, 'model.pkl')

FEATURES = [f'pq{i}' for i in range(1, 11)]   # pq1 … pq10
LABELS = {0: 'Weak', 1: 'Moderate', 2: 'Strong'}
N_SAMPLES = 1500
RANDOM_STATE = 42

np.random.seed(RANDOM_STATE)


def generate_dataset(n: int) -> pd.DataFrame:
    """
    Synthetic dataset with 10 Likert (1-5) features.
    Label is derived from the mean score:
      mean < 2.5  → Weak (0)
      mean < 3.75 → Moderate (1)
      else        → Strong (2)
    Noise is added so the model has something meaningful to learn.
    """
    # Generate base scores from a beta distribution mapped to 1-5
    records = []
    for _ in range(n):
        base = np.random.uniform(1, 5)
        answers = np.clip(
            np.random.normal(loc=base, scale=0.8, size=10).round().astype(int),
            1, 5
        )
        mean_score = answers.mean()
        # Add label noise (~5 %)
        if np.random.random() < 0.05:
            label = np.random.randint(0, 3)
        elif mean_score < 2.5:
            label = 0
        elif mean_score < 3.75:
            label = 1
        else:
            label = 2
        records.append([*answers, label])

    df = pd.DataFrame(records, columns=FEATURES + ['label'])
    return df


def train():
    print("=== Parent-Child Communication Quality — Model Training ===\n")

    # 1. Generate data
    df = generate_dataset(N_SAMPLES)
    print(f"Dataset shape: {df.shape}")
    print("Class distribution:\n", df['label'].value_counts().to_string(), "\n")

    X = df[FEATURES].values
    y = df['label'].values

    # 2. Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # 3. Train GradientBoostingClassifier
    clf = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=4,
        min_samples_split=5,
        random_state=RANDOM_STATE,
    )
    clf.fit(X_train, y_train)

    # 4. Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.4f}\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=list(LABELS.values())))

    # 5. Save model
    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == '__main__':
    train()
