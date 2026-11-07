# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de VOS exécutions.

## 1. Couverture

- Avant (étape A) : 91 % sur `api/`, 6 lignes jamais exécutées.
- Comportements non vérifiés au départ : démarrage sans modèle, modèle retiré de l'état applicatif, panne du modèle, erreurs inattendues et bloc de lancement Uvicorn.
- Après (étape D) : 97,75 % ; les 3 lignes du bloc `if __name__ == "__main__"` restent à surveiller par un autre moyen, car un test importe déjà l'application et ne lance pas volontairement le serveur.

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| --- | --- | --- |
| Texte composé de blancs accepté | `test_limites.py` avec Hypothesis | `field_validator` Pydantic ajoutant le caractère non vide |
| Arrêt au démarrage non vérifié si le modèle manque | Tests d'intégration du chargement | Conservation de `FileNotFoundError`, erreurs internes en HTTP 500 |
| Labels hors contrat possibles dans la réponse | Tests des classes inattendues | Vérification des classes `negative` et `positive` et type limité des labels |
| Erreurs franches du modèle non mesurées | Tests du jeu d'or | Jeu de 20 avis, bilan exact/abstention/erreur et XFAIL strict sur le cas connu |

## 3. Seuil d'abstention

- Points de la courbe (`python src/courbe_seuil.py`) : seuil 0,50 : 58 avis, exactitude 87,9 %, 7 erreurs ; seuil 0,60 : 42 avis, exactitude 95,2 %, 2 erreurs ; seuil 0,70 : 37 avis, exactitude 100 %, 0 erreur.
- Seuil retenu : 0,60 ; 16 avis sur 58 (27,6 %) sont envoyés à un humain sur le jeu de test. Il supprime 5 erreurs tout en conservant 72 % des avis, soit un bon compromis entre automatisation et sécurité.

## 4. Jeu d'or

- Bilan (`python src/bilan_jeu_or.py`) : 8 justes, 11 abstentions, 1 erreur franche déclarée.
- Ces chiffres montrent que le modèle répond peu sur les cas difficiles : ses 8 réponses sont majoritairement correctes, tandis que 11 avis sont renvoyés à un humain. Le XFAIL strict documente l'unique cas franchement erroné connu.

## 5. Outils statiques

- Remarques au départ : Ruff 11 (après la première passe de ruff fix, 9 restaient), puis 0 après corrections finales ; Mypy aucune erreur sur les quatre fichiers API.
- Ruff a surtout détecté les imports, un zip sans `strict`, les noms ambigus et l'import inutilisé. Les défauts dynamiques ont été trouvés par pytest/Hypothesis, non par Mypy : les outils statiques complètent les tests mais ne remplacent pas la validation comportementale.
