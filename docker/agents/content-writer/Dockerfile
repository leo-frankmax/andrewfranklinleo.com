FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/content-writer/ /app/content-writer/
WORKDIR /app/content-writer
CMD ["python", "agent.py"]
