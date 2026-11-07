# Fiche de cadrage : Questions sur le règlement intérieur

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Répondre aux questions des élèves et des parents sur le règlement intérieur en citant les articles pertinents du document officiel.

## Utilisateur final (obligatoire)

Les élèves, parents et personnels administratifs qui cherchent une règle précise sans parcourir l'intégralité du règlement.

## Approche retenue (obligatoire)

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire)

(b) La réponse doit être vérifiable et ancrée dans des articles existants, ce que le RAG permet via des citations. (a) Peu ou pas de questions-réponses étiquetées ne sont nécessaires si les documents officiels sont disponibles. (c) Le coût reste maîtrisé parce que seules les passages pertinents sont envoyés au modèle, au lieu d'une rédaction entièrement libre. (d) Une mauvaise interprétation peut provoquer une décision injuste, donc toute réponse doit indiquer ses sources et transmettre les cas sensibles à un humain.

## Données nécessaires et leur origine (obligatoire)

Version courante du règlement, annexes, procédures internes et historique des questions validées. Les documents seront indexés avec un numéro de version, une date et des références d'article explicites.

## Métrique de succès et seuil d'acceptation (obligatoire)

Mesurer la fidélité aux sources, la présence de citations pertinentes et la satisfaction des utilisateurs ; objectif initial de 90 % de réponses correctes avec citation sur le jeu de questions validé.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une réponse erronée peut modifier une sanction, une absence ou une demande d'inscription. Les cas ambigus, disciplinaires ou sensibles sont transmis à l'administration, qui valide la réponse avant engagement.

## Risques éthiques ou de confidentialité (obligatoire)

Les questions peuvent révéler des données personnelles ou des situations sensibles. Il faut ne stocker que les éléments nécessaires, restreindre les accès aux personnels autorisés et avertir l'utilisateur qu'il ne faut pas communiquer de données personnelles.

## Approche écartée et pourquoi (facultatif)

Un modèle génératif seul est écarté parce qu'il peut produire une réponse plausible mais non conforme à la version officielle, sans lien vérifiable vers un article.

