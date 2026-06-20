FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/qa-validator/ /app/qa-validator/
RUN pip install --no-cache-dir pytest
WORKDIR /app/qa-validator
CMD ["python", "-m", "pytest", "tests/", "-v"]
