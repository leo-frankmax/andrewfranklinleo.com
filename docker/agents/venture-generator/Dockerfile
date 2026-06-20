FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/venture-generator/ /app/venture-generator/
RUN pip install --no-cache-dir pytest
WORKDIR /app/venture-generator
CMD ["python", "-m", "pytest", "tests/", "-v"]
