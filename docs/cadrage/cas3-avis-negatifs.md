# Fiche de cadrage : Priorisation des avis négatifs

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Classifier les avis clients puis prioriser les avis négatifs les plus urgents afin que l'équipe de relation client puisse répondre rapidement.

## Utilisateur final (obligatoire)

Les agents du service client consultent une file triée par sentiment et urgence, avec la possibilité de corriger la priorité.

## Approche retenue (obligatoire)

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire)

(a) Des milliers d'avis associés à des notes ou à des décisions antérieures peuvent fournir des données étiquetées. (c) Le coût par avis est faible une fois le modèle entraîné, ce qui convient à un grand volume quotidien. (d) Rater un avis négatif très urgent peut retardé une résolution, mais une erreur reste corrigible par l'équipe humaine, donc le risque est acceptable si le classement est explicable et révisable.

## Données nécessaires et leur origine (obligatoire)

Avis textuels, note attribuée, catégorie du produit, date, langue et statut de résolution provenant de la plateforme e-commerce, ainsi que des étiquettes validées par les agents sur un échantillon représentatif.

## Métrique de succès et seuil d'acceptation (obligatoire)

Utiliser le F1 macro sur un jeu de test, avec rappel supérieur à 90 % sur la classe négative et un délai médian de prise en charge réduit de 20 % par rapport au classement actuel.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un avis négatif mal classé peut rester sans réponse ou être traité trop tard. Les agents peuvent corriger la priorité et chaque correction alimente un processus de révision avant réentraînement.

## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent contenir des noms, coordonnées ou informations sur des personnes. Il faut anonymiser les données, limiter l'accès aux équipes autorisées, surveiller les biais linguistiques et n'envoyer aucun contenu à un fournisseur tiers sans accord.

## Approche écartée et pourquoi (facultatif)

Les règles par mots-clés sont écartées parce que les formulations négatives sont diverses, ironiques ou contextualisées, et leur maintien devient fragile avec le volume.

