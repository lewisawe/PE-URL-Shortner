# Deploy & Rollback Guide

## Prerequisites
- Docker + Docker Compose
- Git

## Deploy

```bash
git clone https://github.com/lewisawe/PE-URL-Shortner.git
cd PE-URL-Shortner
cp .env.example .env   # edit if needed
docker compose up -d --build
```

Load seed data (first time only):
```bash
docker exec pe-url-shortner-app1-1 uv run python load_csv.py
```

Verify:
```bash
curl http://localhost/health
# {"status": "ok"}
```

## Update (Zero-downtime)

```bash
git pull
docker compose up -d --build --no-deps app1
docker compose up -d --build --no-deps app2
docker compose up -d --build --no-deps app3
```

Rolling restart keeps Nginx routing to healthy instances.

## Rollback

```bash
git log --oneline -5          # find the good commit
git checkout <commit-hash>
docker compose up -d --build
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_NAME` | `hackathon_db` | PostgreSQL database name |
| `DATABASE_HOST` | `localhost` | PostgreSQL host |
| `DATABASE_PORT` | `5432` | PostgreSQL port |
| `DATABASE_USER` | `postgres` | PostgreSQL user |
| `DATABASE_PASSWORD` | `postgres` | PostgreSQL password |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `FLASK_DEBUG` | `false` | Enable debug mode |

## Troubleshooting

**PostgreSQL sequence drift after CSV import**
- Symptom: `duplicate key value violates unique constraint` on INSERT
- Fix: `SELECT setval('user_id_seq', (SELECT MAX(id) FROM "user"));` (repeat for url, event)

**Docker restart policy not triggering**
- Symptom: `docker kill` doesn't restart the container
- Cause: SIGKILL is treated as intentional stop by Docker
- Fix: Use `docker exec <container> sh -c "kill -TERM 1"` to simulate a real crash

**Alertmanager Discord native integration broken (v0.31)**
- Symptom: `unexpected status code 400` from Discord
- Cause: `discord_configs` format changed in Alertmanager v0.31
- Fix: Use a webhook bridge (`notifier.py`) that converts Alertmanager payload to Discord format

**Redis not caching on first deploy**
- Symptom: All cache misses, DB hit on every redirect
- Cause: Seed data loaded with explicit IDs but sequences not reset; app errors silently fell back to DB
- Fix: Reset sequences after CSV load + verify `REDIS_URL` env var is set in container
