FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/site-creator/ /app/site-creator/
WORKDIR /app/site-creator
CMD ["python", "agent.py"]
