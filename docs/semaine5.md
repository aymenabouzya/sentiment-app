# Semaine 5 : interface Streamlit et intégration

## Architecture

- `ui/app.py` affiche uniquement la page et orchestre les composants Streamlit.
- `ui/client.py` encapsule toute la communication HTTP avec `httpx` et traduit les codes de réponse.
- L'API FastAPI reste responsable du chargement du modèle et du calcul du verdict.

## Pourquoi l'interface n'importe-t-elle jamais le modèle ?

L'interface doit pouvoir être remplacée ou déployée séparément sans connaître scikit-learn, les fichiers `.joblib` ou la logique du TP2. Elle reçoit uniquement un verdict et un score depuis l'API. Cette séparation évite les doubles chargements, rend les tests reproductibles avec `TestClient`, et permet de déployer l'API et Streamlit sur des ports ou des machines différents.

## Que montre-t-elle quand le modèle hésite ?

Pour une confiance sous le seuil d'abstention de 0,60, l'API renvoie `INDETERMINE`. Streamlit affiche « Je ne sais pas » avec la confiance et un encadré indiquant qu'un humain doit trancher. Cette abstention est préférable à un verdict forcé : elle évite de présenter une prédiction fragile comme une certitude.

## Que voit l'utilisateur quand l'API tombe ?

Le client tente `/health` à chaque exécution. Si la connexion échoue, Streamlit affiche « API injoignable : lancez d’abord uvicorn api.main:app ». Pour un modèle absent, il affiche « Modèle non chargé ». Les erreurs HTTP sont aussi traduites en avertissement ou message lisible, sans exposer de détails techniques sur la page.

## Lancement local

```powershell
uvicorn api.main:app --reload
streamlit run ui/app.py
```

La page est accessible sur http://localhost:8501 et l'API sur http://127.0.0.1:8000.

## Test du lot

Le fichier `data/avis_exemple.csv` contient six avis. Le lot attendu est résumé ainsi : `{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}`. Le tableau affiché peut être téléchargé sous le nom `resultats.csv`.

## Validation

```powershell
python src/make_demo.py
python src/train.py
python -m pytest -q
ruff check .
mypy api
```
