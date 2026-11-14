"""sentiment_app : classer le sentiment d'un avis en français."""

from importlib.metadata import version

from sentiment_app.predict import predict

__version__ = version("sentiment-app")

__all__ = ["__version__", "predict"]
