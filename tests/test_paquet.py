"""Tests exécutés sur la distribution installée, jamais sur les sources."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_spec = importlib.util.find_spec("sentiment_app")
_origine = (_spec.origin or "").lower() if _spec else ""
if "site-packages" not in _origine and not os.environ.get("VERIFICATION_LIVRABLE"):
    pytest.skip("paquet non installé : python scripts/verifier_livrable.py", allow_module_level=True)

import sentiment_app  # noqa: E402
from sentiment_app import predict  # noqa: E402

COMMANDE = shutil.which("sentiment", path=str(Path(sys.executable).parent))


def test_importe_depuis_le_paquet_installe():
    assert "site-packages" in sentiment_app.__file__.lower()
    assert sentiment_app.__version__ == "1.0.0"
    assert callable(predict)


def test_modele_embarque_et_prediction_positive():
    resultat = predict("Service impeccable, livraison rapide, je recommande")
    assert resultat["label"] == "positive"
    assert 0.0 <= resultat["score"] <= 1.0


def test_prediction_negative():
    resultat = predict("Produit cassé et service client injoignable")
    assert resultat["label"] == "negative"
    assert 0.0 <= resultat["score"] <= 1.0


def test_texte_vide_refuse():
    with pytest.raises(ValueError, match="texte vide"):
        predict("   ")


def test_commande_json():
    assert COMMANDE is not None, "commande sentiment absente de l'environnement installé"
    resultat = subprocess.run(
        [COMMANDE, "--json", "Livraison rapide, très satisfait"],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )
    assert resultat.returncode == 0, resultat.stderr
    corps = json.loads(resultat.stdout)
    assert corps["label"] == "positive"
    assert 0.0 <= corps["score"] <= 1.0


def test_commande_version():
    assert COMMANDE is not None, "commande sentiment absente de l'environnement installé"
    resultat = subprocess.run(
        [COMMANDE, "--version"],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )
    assert resultat.returncode == 0
    assert resultat.stdout.strip() == "sentiment 1.0.0"
