"""Prédiction de sentiment fournie par le paquet installé."""

from functools import lru_cache
from importlib.resources import files
from typing import TypedDict

import joblib


class Resultat(TypedDict):
    label: str
    score: float


@lru_cache(maxsize=1)
def charger_modele():
    """Charge une seule fois le modèle embarqué dans le paquet."""
    modele = files("sentiment_app").joinpath("modele", "sentiment.joblib")
    with modele.open("rb") as fichier:
        return joblib.load(fichier)


def predict(texte: str) -> Resultat:
    """Renvoie le sentiment prédit et sa confiance."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")

    modele = charger_modele()
    etiquette = str(modele.predict([texte])[0])
    score = float(modele.predict_proba([texte]).max())
    return {"label": etiquette, "score": round(score, 4)}
