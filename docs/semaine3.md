# Semaine 3 : l'API, notes du binôme

> Deux questions, quelques phrases chacune. Répondez avec ce que vous avez observé, pas avec le cours.

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib`, plutôt que de démarrer et de répondre 503 ?

Nous avons observé que le `lifespan` charge le modèle avant d'accepter les requêtes. Refuser le démarrage évite un service partiellement disponible qui pourrait répondre 503 à tous les appels et masque une configuration incorrecte dès le déploiement. Le code 503 reste utile si le modèle est retiré ou devient indisponible après l'initialisation.

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par `predict()`. Est-ce redondant ?

Ce n'est pas totalement redondant : Pydantic refuse les erreurs HTTP directement au contrat de l'entrée, notamment les chaînes vides ou les types incorrects avant d'appeler le modèle. La vérification dans `predict()` protège la fonction lorsqu'elle est utilisée directement par un autre appelant ou par un autre module, et fournit une défense en profondeur.
