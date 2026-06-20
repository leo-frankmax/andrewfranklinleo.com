FROM python:3.12-slim
WORKDIR /app
COPY docker/shared/ /app/shared/
COPY docker/mcp-servers/template-mcp/ /app/template-mcp/
COPY templates/ /app/templates/
WORKDIR /app/template-mcp
EXPOSE 3003
CMD ["python", "server.py"]
