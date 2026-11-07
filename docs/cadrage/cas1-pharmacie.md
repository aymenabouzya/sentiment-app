# Fiche de cadrage : Ordonnances incomplètes en pharmacie

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Détecter automatiquement si une ordonnance reçue contient tous les champs obligatoires avant sa validation en pharmacie.

## Utilisateur final (obligatoire)

Le pharmacien vérifie une ordonnance pré-sélectionnée, demande les informations manquantes au patient et confirme la validation finale.

## Approche retenue (obligatoire)

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire)

(a) Les champs obligatoires sont définis par une liste stable et réglementaire, mais il n'est pas nécessaire d'avoir un jeu de données étiquetées pour appliquer ces contrôles. (b) Le résultat est directement vérifiable champ par champ et le pharmacien peut expliquer chaque alerte. (d) Une ordonnance validée à tort peut avoir des conséquences sanitaires graves, donc les décisions strictes et auditables priment sur une prédiction probabiliste.

## Données nécessaires et leur origine (obligatoire)

Modèle d'ordonnance, liste officielle des champs obligatoires, historique anonymisé des ordonnances et règles de validation approuvées par la pharmacie. Les données personnelles et médicales doivent rester sur l'infrastructure de l'établissement.

## Métrique de succès et seuil d'acceptation (obligatoire)

Mesurer le rappel des champs manquants avec un seuil d'au moins 99 % sur les jeux contrôlés, ainsi qu'un taux de faux positifs inférieur à 5 % avant mise en production.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une alerte manquée peut retarder ou rendre dangereuse la délivrance du médicament. Tout résultat est présenté au pharmacien, qui garde seul l'autorisation de valider, et chaque exception est conservée pour audit.

## Risques éthiques ou de confidentialité (obligatoire)

Les ordonnances contiennent des données médicales sensibles. Il faut minimiser les données, contrôler les accès, les chiffrer, appliquer une durée de conservation courte et éviter tout service externe générant une fuite.

## Approche écartée et pourquoi (facultatif)

Un modèle génératif peut mal lire ou inventer un champ absent, sans garantie de vérifiabilité et avec un risque disproportionné pour le contexte sanitaire.

