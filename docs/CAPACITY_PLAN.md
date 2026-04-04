# Capacity Plan

## Current Setup
- 3 × Flask/Gunicorn app instances (t3.medium: 2 vCPU, 4GB RAM)
- 1 × PostgreSQL
- 1 × Redis
- 1 × Nginx

## Measured Limits

| Users | p95 Latency | Error Rate | Bottleneck |
|-------|-------------|------------|------------|
| 50 | 35ms | 0% | None |
| 200 | 1.2s | 0% | App CPU |
| 500 | 3.74s | 0% | App CPU + DB connections |
| ~700 (est.) | >5s | <5% | DB connection pool |

## Where the Limit Is

**~500 concurrent users / ~150 req/sec** on a t3.medium with 3 app instances.

The bottleneck is PostgreSQL connection handling — each Gunicorn worker holds a connection open, and at 500 users the DB starts queuing.

## How to Scale Further

| Target | Action |
|--------|--------|
| 1,000 users | Add 3 more app instances + PgBouncer connection pooler |
| 5,000 users | Upgrade to t3.xlarge, add PostgreSQL read replica for SELECT queries |
| 10,000 users | Move to async workers (Gunicorn + gevent), Redis for session/event queue |
| 50,000+ users | Managed DB (RDS), ElastiCache, horizontal auto-scaling (ECS/K8s) |

## Storage Estimate

- Each URL record: ~500 bytes
- Each event record: ~300 bytes
- 1M URLs + 5M events ≈ ~2GB PostgreSQL storage
- Redis cache (4 short codes per URL × 1M URLs × 200 bytes) ≈ ~800MB RAM
