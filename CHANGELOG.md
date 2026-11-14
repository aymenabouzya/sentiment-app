# Journal des modifications

## [1.0.0] - 2026-11-14

- Ajoute le paquet Python installable `sentiment-app` et sa fonction `predict`.
- Embarque le modèle de sentiment dans la roue distribuée.
- Ajoute la commande `sentiment`, avec sorties texte et JSON.
- Documente l'installation, l'utilisation et les limites du modèle.
- Limite connue : les avis ironiques, mitigés et hors domaine peuvent être mal
  classés; le score ne garantit pas l'exactitude.
