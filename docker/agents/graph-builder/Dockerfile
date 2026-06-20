FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/graph-builder/ /app/graph-builder/
RUN pip install --no-cache-dir pytest
WORKDIR /app/graph-builder
CMD ["python", "-m", "pytest", "tests/", "-v"]
