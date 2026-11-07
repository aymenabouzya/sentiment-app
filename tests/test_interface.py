from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from api.main import app
from ui import client


def executer(monkeypatch):
    session = TestClient(app)
    session.__enter__()
    monkeypatch.setattr(client, "creer_session", lambda: session)
    page = AppTest.from_file("ui/app.py").run(timeout=30)
    return page, session


def test_page_titre_et_api_prete(monkeypatch):
    page, session = executer(monkeypatch)
    assert page.title[0].value == "Analyse de sentiment des avis"
    assert page.caption[0].value == "API prête : tfidf-logreg (TP2, models/sentiment.joblib)"
    session.__exit__(None, None, None)


def test_interface_avis_positif(monkeypatch):
    page, session = executer(monkeypatch)
    page.text_area[0].input("Livraison rapide, produit conforme, très satisfait")
    page.button[0].click().run(timeout=30)
    assert page.metric[0].label == "Avis positif"
    assert page.metric[0].value == "78%"
    session.__exit__(None, None, None)


def test_interface_avis_negatif(monkeypatch):
    page, session = executer(monkeypatch)
    page.text_area[0].input("Produit cassé et service injoignable, à fuir")
    page.button[0].click().run(timeout=30)
    assert page.metric[0].label == "Avis négatif"
    session.__exit__(None, None, None)


def test_interface_abstention(monkeypatch):
    page, session = executer(monkeypatch)
    page.text_area[0].input("xqzvb wlkptr grombu")
    page.button[0].click().run(timeout=30)
    assert page.metric[0].label.startswith("Je ne sais pas")
    assert len(page.info) >= 1
    session.__exit__(None, None, None)


def test_interface_texte_refuse(monkeypatch):
    page, session = executer(monkeypatch)
    page.text_area[0].input("   ")
    page.button[0].click().run(timeout=30)
    assert len(page.warning) >= 1
    assert client.REFUS in page.warning[0].value
    session.__exit__(None, None, None)
