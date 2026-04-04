# Runbook: PE URL Shortener

## Alert: ServiceDown

**Trigger:** An app instance has been unreachable for >15 seconds.

**Steps:**
1. Check which instance is down:
   ```bash
   docker ps --filter "name=pe-url-shortner-app"
   ```
2. Check logs for crash reason:
   ```bash
   docker logs pe-url-shortner-app1-1 --tail 50
   ```
3. Restart the instance:
   ```bash
   docker start pe-url-shortner-app1-1
   ```
4. Verify recovery:
   ```bash
   curl http://localhost/health
   ```
5. Check Grafana → "Active Instances" panel shows 3.

---

## Alert: HighErrorRate

**Trigger:** 5xx error rate > 5% for 2 minutes.

**Steps:**
1. Check error logs:
   ```bash
   docker logs pe-url-shortner-app1-1 2>&1 | grep ERROR | tail -20
   ```
2. Check DB connectivity:
   ```bash
   docker exec pe-url-shortner-db-1 pg_isready
   ```
3. Check Redis:
   ```bash
   docker exec pe-url-shortner-redis-1 redis-cli ping
   ```
4. If DB is down, restart it:
   ```bash
   docker compose restart db
   ```
5. Monitor error rate on Grafana → "Error Rate" panel until it drops to 0.

---

## Alert: HighLatency

**Trigger:** p95 latency > 3s for 2 minutes.

**Steps:**
1. Check active connections and load:
   ```bash
   docker stats --no-stream
   ```
2. Check Redis cache hit rate:
   ```bash
   docker exec pe-url-shortner-redis-1 redis-cli info stats | grep keyspace
   ```
3. If cache hit rate is low, the DB is being hammered. Scale up:
   ```bash
   docker compose up -d --scale app=5
   ```
4. Monitor Grafana → "p95 Latency" panel until it drops below 1s.

---

## General Recovery

```bash
# Full restart
cd ~/PE-URL-Shortner
docker compose down && docker compose up -d

# View all logs
docker compose logs --tail=100

# Check all container health
docker ps --filter "name=pe-url-shortner"
```
