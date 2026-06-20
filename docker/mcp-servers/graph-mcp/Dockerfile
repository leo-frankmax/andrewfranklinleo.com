FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY mcp-servers/graph-mcp/ /app/graph-mcp/
WORKDIR /app/graph-mcp
EXPOSE 3004
CMD ["python", "server.py"]
