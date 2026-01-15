# Day 55 — APIs and Containerization with Docker (Companion Guide)

## Learning objectives
- Containerize a FastAPI model service with Docker
- Manage dependencies, environment variables, and ports
- Build, run, and test images locally

## Why this matters
Containers provide portable, reproducible runtime environments for services.

## Core concepts and examples
### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and run
```bash
docker build -t ds-model:latest .
docker run -p 8000:8000 --env-file .env ds-model:latest
```

## Common pitfalls
- Not pinning package versions; non-reproducible builds
- Fat images; prefer slim bases and multi-stage builds
- Ignoring health checks and logging

## Practice exercises
1) Containerize the Day 44 FastAPI service
2) Add a health endpoint and docker HEALTHCHECK
3) Optimize image size with multi-stage builds

## Further reading
- Docker docs: https://docs.docker.com
