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

**App won't start**
```bash
docker compose logs app1
```

**DB connection refused**
```bash
docker compose ps db   # check db is healthy
docker exec pe-url-shortner-db-1 pg_isready
```

**Redis not caching**
```bash
docker exec pe-url-shortner-redis-1 redis-cli ping
docker exec pe-url-shortner-redis-1 redis-cli info stats | grep keyspace
```

**Port 80 already in use**
```bash
sudo lsof -i :80
# change ports in docker-compose.yml
```
