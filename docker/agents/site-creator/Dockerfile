FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/site-creator/ /app/site-creator/
RUN pip install --no-cache-dir pytest
WORKDIR /app/site-creator
CMD ["python", "-m", "pytest", "tests/", "-v"]
