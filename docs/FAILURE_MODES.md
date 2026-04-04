# Failure Modes Documentation

## Error Handling

All errors return JSON responses with an `error` field:

```json
{"error": "Description of what went wrong"}
```

### HTTP Status Codes

| Code | Meaning | When it happens |
|------|---------|-----------------|
| 400 | Bad Request | Missing required fields, invalid JSON, invalid URL format |
| 404 | Not Found | Resource doesn't exist (user, URL, short code) |
| 405 | Method Not Allowed | Wrong HTTP method for endpoint |
| 410 | Gone | URL exists but is deactivated |
| 500 | Internal Server Error | Database errors, unexpected exceptions |

### Common Failure Scenarios

#### 1. Database Connection Lost
- **Symptom**: 500 errors on all requests
- **Response**: `{"error": "connection to server failed..."}`
- **Recovery**: App auto-reconnects on next request via connection pooling

#### 2. Invalid User ID
- **Symptom**: 404 when creating URLs
- **Response**: `{"error": "User not found"}`
- **Fix**: Verify user exists before creating URLs

#### 3. Duplicate Short Code (rare)
- **Symptom**: 500 on URL creation
- **Response**: `{"error": "Failed to generate unique short code"}`
- **Mitigation**: App retries 5 times with different codes

#### 4. Inactive URL Access
- **Symptom**: 410 Gone on redirect
- **Response**: `{"error": "URL is inactive"}`
- **Fix**: Reactivate URL via PUT /urls/<id>

## Chaos Engineering

### Docker Auto-Restart

The app runs with `restart: always` policy:

```yaml
services:
  app:
    restart: always
```

**Test it:**
```bash
# Start the stack
docker compose up -d

# Kill the app container
docker kill pe-url-shortner-app-1

# Watch it restart automatically
docker ps -a
```

### Health Check

Load balancers should poll `GET /health`:
- Returns `{"status": "ok"}` with 200 when healthy
- Any other response = unhealthy, don't route traffic

## Recovery Procedures

1. **App crash**: Docker restarts automatically (< 5 seconds)
2. **DB crash**: App returns 500s until DB recovers, then auto-reconnects
3. **Out of memory**: Docker restarts, consider scaling horizontally
