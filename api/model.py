"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() de src/predict.py, qui charge models/sentiment.joblib une seule fois.
"""
import sys
from pathlib import Path
from typing import Literal, TypedDict

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from predict import charger_modele  # noqa: E402  (fonctions du TP2)
from predict import predict as _predict  # noqa: E402

SEUIL_ABSTENTION = 0.60
SentimentLabel = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]


class SentimentPrediction(TypedDict):
    label: SentimentLabel
    score: float
    text: str


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        pipeline = charger_modele()
        classes = {str(label) for label in pipeline.classes_}
        if classes != {"negative", "positive"}:
            raise RuntimeError(f"Classes inattendues du modèle : {sorted(classes)}")

    def predict(self, text: str) -> SentimentPrediction:
        """Renvoie une étiquette du contrat ou INDETERMINE sous le seuil."""
        result = _predict(text)
        if result["score"] < SEUIL_ABSTENTION:
            label: SentimentLabel = "INDETERMINE"
        elif result["label"] == "positive":
            label = "POSITIVE"
        else:
            label = "NEGATIVE"
        return {"label": label, "score": result["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    """Construit le classifier (le cache de chargement est dans src/predict.py)."""
    return SentimentClassifier()
