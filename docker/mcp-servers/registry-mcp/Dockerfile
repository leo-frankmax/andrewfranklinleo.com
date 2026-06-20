FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY mcp-servers/registry-mcp/ /app/registry-mcp/
WORKDIR /app/registry-mcp
EXPOSE 3005
CMD ["python", "server.py"]
