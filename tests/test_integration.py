"""Tests d'intégration : l'API telle qu'elle tourne vraiment (TP4, étape D). À COMPLÉTER.

Les tests du TP3 vérifient des réponses ; ceux-ci vérifient le démarrage de l'API
et son comportement quand le modèle manque ou tombe en panne.
"""
from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


def test_demarrage_reel_charge_le_modele():
    """D.1 : un client ouvert par « with » exécute le lifespan."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        reponse = client.get("/health")
    assert reponse.status_code == 200
    assert "TP2" in reponse.json()["model"]


def test_modele_absent_refuse_le_demarrage(monkeypatch):
    from fastapi.testclient import TestClient

    import predict
    from api.main import app

    monkeypatch.setattr(predict, "MODELE", Path("model-inexistant.joblib"))
    predict.charger_modele.cache_clear()
    with pytest.raises(FileNotFoundError):
        with TestClient(app):
            pass


def test_modele_non_charge_retourne_503():
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        monkeypatch_client = getattr(client.app.state, "classifier", None)
        del client.app.state.classifier
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json={"text": "livraison rapide"}).status_code == 503
        client.app.state.classifier = monkeypatch_client


@pytest.mark.parametrize("exception", [RuntimeError("panne technique"), ValueError("bug interne")])
def test_modele_en_panne_retourne_500(exception):
    from fastapi.testclient import TestClient

    from api.main import app

    class ModeleEnPanne:
        model_name = "modele factice"

        def predict(self, text):
            raise exception

    with TestClient(app) as client:
        client.app.state.classifier = ModeleEnPanne()
        reponse = client.post("/predict", json={"text": "livraison rapide"})
    assert reponse.status_code == 500
    assert "panne technique" not in reponse.text
    assert "bug interne" not in reponse.text


def test_classes_inattendues_refusent_le_demarrage(monkeypatch):
    import api.model

    class FauxPipeline:
        classes_ = ["negative", "neutral"]

    monkeypatch.setattr(api.model, "charger_modele", lambda: FauxPipeline())
    with pytest.raises(RuntimeError, match="Classes inattendues"):
        api.model.SentimentClassifier()


# À écrire (étape D) :
# D.2 modèle absent : chemin du modèle redirigé (monkeypatch), cache vidé
#     (charger_modele.cache_clear()), l'API refuse de démarrer (FileNotFoundError) ;
# D.3 modèle non chargé : l'API démarrée, modèle retiré de app.state, 503 sur /health et /predict ;
# D.4 modèle en panne : predict lève RuntimeError, puis ValueError("bug interne") :
#     500 dans les deux cas, sans le message interne dans la réponse.
# Utilisez monkeypatch.setattr pour toute modification : il restaure l'état à la fin du test.
