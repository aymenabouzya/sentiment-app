"""Interface Streamlit du service d'analyse de sentiment."""

import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st

DEFAULT_API_URL = "http://127.0.0.1:8000"


def api_url() -> str:
    """Retourne l'URL configurée sans slash final."""
    return os.getenv("API_URL", DEFAULT_API_URL).rstrip("/")


def verifier_api(base_url: str | None = None, timeout: float = 5.0) -> bool:
    """Vérifie que l'API est joignable et chargée."""
    response = requests.get(f"{base_url or api_url()}/health", timeout=timeout)
    response.raise_for_status()
    return response.json().get("status") == "OK"


def predire_sentiment(texte: str, base_url: str | None = None, timeout: float = 10.0) -> dict[str, Any]:
    """Appelle POST /predict et renvoie la réponse JSON."""
    response = requests.post(
        f"{base_url or api_url()}/predict",
        json={"text": texte},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def afficher_prediction(resultat: dict[str, Any]) -> None:
    """Affiche une prédiction avec une présentation adaptée à son label."""
    label = str(resultat["label"])
    score = float(resultat["score"])
    if label == "POSITIVE":
        st.success(f"**POSITIVE** — confiance {score:.1%}")
    elif label == "NEGATIVE":
        st.error(f"**NEGATIVE** — confiance {score:.1%}")
    else:
        st.warning(f"**INDETERMINE** — confiance {score:.1%}")
    st.progress(max(0.0, min(score, 1.0)))


def main() -> None:
    """Construit et lance l'interface Streamlit."""
    st.set_page_config(page_title="Sentiment Analysis", page_icon="💬", layout="centered")
    st.title("Analyse de sentiment")
    st.caption("Application Streamlit reliée à l'API FastAPI — TP5")

    with st.sidebar:
        st.subheader("Connexion")
        base_url = st.text_input("URL de l'API", value=api_url())
        try:
            api_disponible = verifier_api(base_url)
            if api_disponible:
                st.success("API disponible")
            else:
                st.error("API démarrée, modèle indisponible")
        except requests.RequestException as exc:
            api_disponible = False
            st.error("API inaccessible")
            st.caption(str(exc))

    texte = st.text_area(
        "Avis à analyser",
        placeholder="Écrivez votre avis en français…",
        height=160,
        max_chars=2000,
    )

    if "historique" not in st.session_state:
        st.session_state.historique = []

    if st.button("Analyser", type="primary", disabled=not api_disponible):
        if not texte.strip():
            st.error("Veuillez saisir un avis.")
        else:
            try:
                with st.spinner("Analyse en cours…"):
                    resultat = predire_sentiment(texte, base_url)
                afficher_prediction(resultat)
                st.session_state.historique.insert(
                    0,
                    {
                        "heure": datetime.now().strftime("%H:%M:%S"),
                        "texte": texte[:80],
                        "label": resultat["label"],
                        "score": resultat["score"],
                    },
                )
            except requests.HTTPError as exc:
                reponse = exc.response
                detail = reponse.json().get("detail") if reponse is not None else None
                st.error(detail or "Erreur retournée par l'API")
            except requests.RequestException as exc:
                st.error(f"Impossible de joindre l'API : {exc}")

    if st.session_state.historique:
        st.divider()
        st.subheader("Historique de la session")
        st.dataframe(st.session_state.historique, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
