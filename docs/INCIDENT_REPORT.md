# Incident Report: Phantom High Error Rate

## Summary
Prometheus dashboards showed a sustained 404 error rate of ~8 req/s, despite all application instances being healthy and returning correct responses.

## Timeline
- **17:01** — High 404 error rate observed in Prometheus metrics
- **17:05** — Confirmed `/health`, `/users`, `/urls` all returning 200 on app instances
- **17:08** — Identified `nginx:80` scrape target as source of inflated error counts
- **17:12** — Removed `nginx` scrape job from `prometheus.yml`
- **17:16** — Deployed fix, restarted Prometheus
- **17:21** — Error rate decayed to 0 after 5-minute `rate()` window passed

## Root Cause
Prometheus was configured to scrape `nginx:80` as a metrics target. Since nginx doesn't expose `/metrics`, the request was proxied to a random Flask backend via round-robin. This caused:

1. Flask metrics were double-counted under both the `app` and `nginx` instance labels
2. Round-robin meant each scrape could hit a different backend, causing Prometheus to see counter resets
3. `rate()` interpreted these resets as new errors, inflating the 404 rate from 0 to ~8/s

## Resolution
Removed the `nginx` scrape job from `prometheus.yml`. The three Flask app instances (`app1:5000`, `app2:5000`, `app3:5000`) are already scraped directly, which is the correct approach.

## Lessons Learned
- Only scrape targets that expose their own metrics endpoint
- Proxied metrics create phantom counters and misleading rates
- Always verify error sources by comparing per-instance rates before investigating application code
