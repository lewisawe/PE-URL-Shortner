# PE URL Shortener

A production-grade URL shortener built for the MLH Production Engineering Hackathon.

**Stack:** Flask · Peewee ORM · PostgreSQL · Redis · Nginx · Docker

## Architecture

```
Internet → Nginx (port 80)
              ↓ round-robin
    ┌─────────────────────┐
    │  app1  app2  app3   │  (Flask + Gunicorn)
    └─────────────────────┘
         ↓           ↓
    PostgreSQL      Redis
    (persistent)   (cache)
```

## Quick Start

```bash
git clone https://github.com/lewisawe/PE-URL-Shortner.git
cd PE-URL-Shortner
cp .env.example .env
docker compose up -d --build
docker exec pe-url-shortner-app1-1 uv run python load_csv.py
curl http://localhost/health
```

## Documentation

- [API Reference](docs/API.md)
- [Deploy & Rollback Guide](docs/DEPLOY.md)
- [Failure Modes](docs/FAILURE_MODES.md)
- [Bottleneck Report](docs/BOTTLENECK_REPORT.md)
- [Runbook](docs/RUNBOOK.md)
- [Decision Log](docs/DECISION_LOG.md)
- [Capacity Plan](docs/CAPACITY_PLAN.md)

## Running Tests

```bash
uv sync
createdb hackathon_test
uv run pytest tests/ --cov=app
```

## Load Test Results

| Scenario | Users | p95 Latency | Error Rate | req/sec |
|----------|-------|-------------|------------|---------|
| Bronze | 50 | 35ms | 0% | 77 |
| Silver | 200 | 1.2s | 0% | 74 |
| Gold | 500 | 3.74s | 0% | **143** |

## Quest Progress

- 🛡️ **Reliability** — Bronze ✅ Silver ✅ Gold ✅
- 🚀 **Scalability** — Bronze ✅ Silver ✅ Gold ✅
