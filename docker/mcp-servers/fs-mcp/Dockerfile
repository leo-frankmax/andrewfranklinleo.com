FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
COPY mcp-servers/fs-mcp/ /app/fs-mcp/

RUN pip install --no-cache-dir /app/fs-mcp

WORKDIR /app/fs-mcp

EXPOSE 3001

CMD ["python", "server.py"]
