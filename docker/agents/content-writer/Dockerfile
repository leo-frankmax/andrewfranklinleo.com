FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/content-writer/ /app/content-writer/
RUN pip install --no-cache-dir pytest
WORKDIR /app/content-writer
CMD ["python", "-m", "pytest", "tests/", "-v"]
