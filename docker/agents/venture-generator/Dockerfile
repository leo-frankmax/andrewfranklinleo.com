FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/venture-generator/ /app/venture-generator/
WORKDIR /app/venture-generator
CMD ["python", "agent.py"]
