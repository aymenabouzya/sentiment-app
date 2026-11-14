# sentiment-app

`sentiment-app` est un paquet Python qui classe en français un avis client comme
`positive` ou `negative` et fournit un score de confiance.

## Installation

Installez la roue publiée avec la release GitHub, ou construisez-la depuis les
sources du dépôt :

```powershell
python -m pip install .\dist\sentiment_app-1.0.0-py3-none-any.whl
```

Le paquet nécessite Python 3.11 ou plus récent. La roue contient le modèle
entraîné et installe scikit-learn 1.5 ainsi que joblib.

## Utilisation Python

```python
from sentiment_app import predict

print(predict("Livraison rapide, produit conforme, très satisfait"))
# {'label': 'positive', 'score': 0.79}
```

Le score est la confiance estimée par le modèle, pas une garantie d'exactitude.
Un avis vide ou composé d'espaces lève `ValueError`.

## Ligne de commande

```powershell
sentiment "Produit cassé, je ne recommande pas"
sentiment --json "Livraison rapide, très satisfait"
sentiment --version
```

## Limites connues

Le modèle est entraîné sur un jeu de démonstration de taille limitée. Il peut
mal interpréter l'ironie, les négations complexes, les avis mitigés et les
domaines absents de ses données. Vérifiez les avis importants et interprétez le
score comme une estimation, non comme une certitude.
