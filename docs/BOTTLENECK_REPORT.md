# Bottleneck Report

## What Was Slow

**Before optimization:** Single app instance handling all requests directly hit PostgreSQL on every redirect.

At 500 concurrent users, p95 latency was **>4s** and the DB became the bottleneck — every redirect required a full SQL query.

## What We Fixed

### 1. Redis Caching (Biggest Win)
Cached URL lookups in Redis with a 5-minute TTL.

| Metric | Before Cache | After Cache |
|--------|-------------|-------------|
| DB queries per redirect | 1 | 0 (cache hit) |
| Cache hit rate @ 500 users | — | ~50% |
| p95 latency | >4s | 3.74s |

The first request for a short code hits the DB and warms the cache. All subsequent requests are served from memory.

### 2. Horizontal Scaling (Nginx + 3 App Instances)
Distributed load across 3 app containers behind Nginx round-robin.

- Single instance: saturated at ~150 concurrent users
- 3 instances: handles 500 concurrent users with 0% errors

### 3. Results Summary

| Test | Users | p95 Latency | Error Rate | req/sec |
|------|-------|-------------|------------|---------|
| Bronze | 50 | 35ms | 0% | ~77 |
| Silver | 200 | 1.2s | 0% | ~74 |
| Gold | 500 | 3.74s | 0% | **143** |

## Remaining Bottleneck

The DB is still the weak link for write-heavy operations (POST /urls, event logging). Next steps would be:
- Connection pooling (PgBouncer)
- Async event logging (write to Redis queue, flush to DB in background)
- Read replicas for SELECT queries
