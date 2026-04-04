# Decision Log

## Why Flask?
Lightweight, fast to build with, and the hackathon template was already Flask. Peewee ORM pairs well with it for simple models without the overhead of SQLAlchemy.

## Why PostgreSQL?
Relational data with clear FK relationships (users → urls → events). ACID compliance ensures no lost clicks or duplicate short codes under concurrent load.

## Why Redis?
The redirect endpoint (`GET /<short_code>`) is the hottest path — called on every link click. Caching URL lookups in Redis eliminates DB reads entirely after the first hit, dropping p95 latency from >4s to <1s at 500 users.

## Why Nginx?
Simple, battle-tested reverse proxy. Round-robin load balancing across 3 app instances with zero config overhead. Handles connection queuing so app workers aren't overwhelmed.

## Why 3 App Instances?
A t3.medium has 2 vCPUs. Gunicorn sync workers block on I/O (DB queries). 3 instances × 1 worker each = enough concurrency to saturate the CPU without context-switch overhead. Tested: 1 instance saturates at ~150 users, 3 instances handles 500 with 0% errors.

## Why Prometheus + Grafana over Datadog/New Relic?
Open source, self-hosted, no API key or billing required. Prometheus scrapes `/metrics` directly from Flask via `prometheus-flask-exporter`. Grafana visualizes it with zero cost.

## Why Alertmanager + custom Discord bridge?
Alertmanager's native Discord integration had breaking changes in v0.31. A 20-line Flask bridge converts Alertmanager's webhook payload to Discord's format reliably.

## Why `restart: always` in Docker Compose?
Ensures containers auto-recover from crashes without operator intervention — core requirement for the Reliability Gold tier chaos demo.
