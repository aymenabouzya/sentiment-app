FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi==0.115.* uvicorn==0.30.* pydantic==2.9.* joblib==1.4.* pandas==2.2.* scikit-learn==1.5.*

COPY api ./api
COPY src ./src
COPY models ./models

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
