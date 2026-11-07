import httpx
from fastapi.testclient import TestClient

from api.main import app
from ui import client


def test_creer_session_base_url():
    session = client.creer_session()
    assert isinstance(session, httpx.Client)
    assert str(session.base_url).rstrip("/") == client.API_URL
    session.close()


def test_sante_api_preparee():
    with TestClient(app) as session:
        reponse = client.sante(session)
    assert reponse.ok
    assert reponse.message == "tfidf-logreg (TP2, models/sentiment.joblib)"


def test_predire_positif():
    with TestClient(app) as session:
        reponse = client.predire(session, "Livraison rapide, produit conforme, très satisfait")
    assert reponse.ok
    assert reponse.label == "POSITIVE"
    assert 0 <= reponse.score <= 1


def test_predire_negatif():
    with TestClient(app) as session:
        reponse = client.predire(session, "Produit cassé et service injoignable, à fuir")
    assert reponse.ok
    assert reponse.label == "NEGATIVE"


def test_predire_abstention():
    with TestClient(app) as session:
        reponse = client.predire(session, "xqzvb wlkptr grombu")
    assert reponse.ok
    assert reponse.label == "INDETERMINE"


def test_predire_texte_refuse():
    with TestClient(app) as session:
        reponse = client.predire(session, "   ")
    assert not reponse.ok
    assert reponse.message == client.REFUS


def test_predire_lot_et_resumer():
    textes = [line.strip() for line in open("data/avis_exemple.csv", encoding="utf-8").read().splitlines()[1:] if line.strip()]
    with TestClient(app) as session:
        reponses = client.predire_lot(session, textes)
    resume = client.resumer(reponses)
    assert resume == {"INDETERMINE": 1, "NEGATIVE": 2, "POSITIVE": 3}
