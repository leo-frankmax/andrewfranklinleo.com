FROM python:3.12-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY mcp-servers/content-mcp/ /app/content-mcp/
WORKDIR /app/content-mcp
EXPOSE 3002
CMD ["python", "server.py"]
