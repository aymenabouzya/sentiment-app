from unittest.mock import Mock

import pytest


@pytest.fixture
def ui_module(monkeypatch):
    """Importe l'interface sans exécuter une session Streamlit réelle."""
    monkeypatch.setenv("API_URL", "http://api.test:8000/")
    import ui.app as module

    return module


def test_api_url_depuis_environnement(ui_module, monkeypatch):
    monkeypatch.setenv("API_URL", "http://localhost:9000/")
    assert ui_module.api_url() == "http://localhost:9000"


def test_verifier_api(ui_module, monkeypatch):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"status": "OK"}
    post = Mock(return_value=response)
    monkeypatch.setattr(ui_module.requests, "get", post)

    assert ui_module.verifier_api("http://api.test:8000") is True
    post.assert_called_once_with("http://api.test:8000/health", timeout=5.0)


def test_predire_sentiment(ui_module, monkeypatch):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"label": "POSITIVE", "score": 0.82, "text": "bon film"}
    post = Mock(return_value=response)
    monkeypatch.setattr(ui_module.requests, "post", post)

    resultat = ui_module.predire_sentiment("bon film", "http://api.test:8000")

    assert resultat["label"] == "POSITIVE"
    post.assert_called_once_with(
        "http://api.test:8000/predict",
        json={"text": "bon film"},
        timeout=10.0,
    )
