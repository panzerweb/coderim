# Backend image for a trusted-code contest. Frontend is a separate Static Site.
FROM node:22-bookworm-slim AS node_runtime
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    RELAY_MODE=contest RELAY_EXECUTOR=local RELAY_RUNTIME=/var/data/relay
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ openjdk-17-jdk-headless ca-certificates libatomic1 gosu \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 relay
COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend /app/backend
COPY problems /app/problems
COPY tools /app/tools
COPY scripts/container-start.sh /usr/local/bin/relay-start
RUN chmod 755 /usr/local/bin/relay-start \
    && mkdir -p /var/data/relay && chown relay:relay /var/data/relay
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/relay-start"]
