FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY agents/graph-builder/ /app/graph-builder/
ENV PYTHONPATH=/app
WORKDIR /app/graph-builder
CMD ["python", "agent.py"]
