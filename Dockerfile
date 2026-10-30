FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install curl for container-level health check (Tugas D)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app.py .

EXPOSE 5000

# Tugas D: Docker native HEALTHCHECK instruction
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
