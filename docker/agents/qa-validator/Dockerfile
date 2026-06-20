FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/qa-validator/ /app/qa-validator/
ENV PYTHONPATH=/app
WORKDIR /app/qa-validator
CMD ["python", "agent.py"]
