FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2 (compiled) — psycopg2-binary avoids needing these,
# but libpq is still required at runtime on slim images.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY dashboard/requirements.txt ./dashboard/requirements.txt
RUN pip install --no-cache-dir -r dashboard/requirements.txt

# App code + server (DB/auth/queries) + the processed data the one-time seed
# needs. Raw scraper output, notebooks, and the thesis chapters are not
# needed at runtime and are excluded via .dockerignore to keep the image small.
COPY server/ ./server/
COPY dashboard/ ./dashboard/
COPY data/processed/ ./data/processed/
COPY data/runs/ ./data/runs/
COPY pipeline/ ./pipeline/
COPY docker-entrypoint.sh ./

RUN chmod +x docker-entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["./docker-entrypoint.sh"]
