# Semaine 5 : interface Streamlit et intégration

## Interface

L'application se trouve dans `ui/app.py`. Elle permet :

- de saisir un avis de moins de 2000 caractères ;
- de vérifier la disponibilité de l'API ;
- de lancer une prédiction ;
- d'afficher POSITIVE, NEGATIVE ou INDETERMINE avec le score ;
- de conserver l'historique de la session.

## Configuration

L'adresse par défaut est `http://127.0.0.1:8000`. Elle peut être remplacée par la variable `API_URL` ou depuis la barre latérale.

## Lancement local

```powershell
# Terminal 1
.venv\Scripts\Activate.ps1
uvicorn api.main:app --reload

# Terminal 2
.venv\Scripts\Activate.ps1
streamlit run ui/app.py
```

## Lancement Docker

```powershell
docker compose up --build
```

- API : http://localhost:8000/docs
- Interface : http://localhost:8501

## Tests

L'interface possède des tests unitaires pour la construction de l'URL, le contrôle de santé et l'appel de prédiction.
