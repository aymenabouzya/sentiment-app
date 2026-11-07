"""Client HTTP entre l'interface Streamlit et l'API FastAPI (TP5)."""

import os
from collections import Counter
from dataclasses import dataclass

import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
VERDICTS = {
    "POSITIVE": "Avis positif",
    "NEGATIVE": "Avis négatif",
    "INDETERMINE": "Je ne sais pas : à faire vérifier par un humain",
}
REFUS = "Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères"
SANS_MODELE = "Modèle non chargé"
INJOIGNABLE = "API injoignable : lancez d’abord uvicorn api.main:app"
ERREUR_API = "Erreur interne de l'API"


@dataclass
class Reponse:
    """Verdict ou message prêt à afficher dans Streamlit."""

    ok: bool
    label: str | None = None
    score: float | None = None
    message: str = ""


def creer_session() -> httpx.Client:
    """Crée la connexion HTTP utilisée par la page."""
    return httpx.Client(base_url=API_URL, timeout=10.0)


def sante(session: httpx.Client) -> Reponse:
    """Interroge GET /health sans exposer les détails HTTP à la page."""
    try:
        reponse = session.get("/health")
    except httpx.RequestError:
        return Reponse(ok=False, message=INJOIGNABLE)
    if reponse.status_code == 200:
        corps = reponse.json()
        return Reponse(ok=True, message=str(corps.get("model", "modèle inconnu")))
    if reponse.status_code == 503:
        return Reponse(ok=False, message=SANS_MODELE)
    return Reponse(ok=False, message=f"{ERREUR_API} (code {reponse.status_code})")


def predire(session: httpx.Client, texte: str) -> Reponse:
    """Envoie un avis à POST /predict et traduit son résultat ou son erreur."""
    try:
        reponse = session.post("/predict", json={"text": texte})
    except (httpx.RequestError, httpx.HTTPError):
        return Reponse(ok=False, message=INJOIGNABLE)

    if reponse.status_code == 200:
        corps = reponse.json()
        return Reponse(
            ok=True,
            label=str(corps["label"]),
            score=float(corps["score"]),
        )
    if reponse.status_code == 422:
        return Reponse(ok=False, message=REFUS)
    if reponse.status_code == 503:
        return Reponse(ok=False, message=SANS_MODELE)
    return Reponse(ok=False, message=f"{ERREUR_API} (code {reponse.status_code})")


def predire_lot(session: httpx.Client, textes: list[str]) -> list[Reponse]:
    """Prédit chaque avis, dans l'ordre, en conservant une réponse par ligne."""
    return [predire(session, texte) for texte in textes]


def resumer(reponses: list[Reponse]) -> dict[str, int]:
    """Compte uniquement les verdicts positifs, négatifs ou indéterminés."""
    comptes: Counter[str] = Counter(r.label for r in reponses if r.ok and r.label in VERDICTS)
    return {
        label: comptes[label]
        for label in ("INDETERMINE", "NEGATIVE", "POSITIVE")
    }
