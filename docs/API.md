# URL Shortener — API Documentation

Base URL: `http://<host>/`

---

## Health

### `GET /health`
Returns service status.

**Response `200`**
```json
{"status": "ok"}
```

---

## Users

### `GET /users`
List all users. Supports pagination.

**Query params:** `page`, `per_page`

**Response `200`**
```json
[{"id": 1, "username": "alice", "email": "alice@example.com", "created_at": "2025-01-01T00:00:00"}]
```

### `GET /users/<id>`
Get user by ID.

**Response `200` / `404`**

### `POST /users`
Create a user.

**Body**
```json
{"username": "alice", "email": "alice@example.com"}
```

**Response `201` / `400`**

### `PUT /users/<id>`
Update a user.

**Body** (any subset)
```json
{"username": "new_name", "email": "new@example.com"}
```

**Response `200` / `404`**

### `POST /users/bulk`
Bulk import users from CSV file.

**Body:** `multipart/form-data` with `file` field (users.csv)

**Response `201`**
```json
{"count": 400}
```

---

## URLs

### `GET /urls`
List URLs. Supports filtering and pagination.

**Query params:** `page`, `per_page`, `user_id`, `is_active`

**Response `200`**
```json
[{"id": 1, "user_id": 1, "short_code": "MQPKPq", "original_url": "https://...", "title": "...", "is_active": true, "created_at": "...", "updated_at": "..."}]
```

### `GET /urls/<id>`
Get URL by ID.

**Response `200` / `404`**

### `POST /urls`
Create a short URL.

**Body**
```json
{"user_id": 1, "original_url": "https://example.com", "title": "Optional title"}
```

**Response `201` / `400` / `404`**

### `PUT /urls/<id>`
Update URL details.

**Body** (any subset)
```json
{"title": "New title", "is_active": false}
```

**Response `200` / `404`**

### `DELETE /urls/<id>`
Delete a URL and its events.

**Response `200` / `404`**

### `GET /<short_code>`
Redirect to original URL.

**Response `302` / `404`**

### `GET /urls/<short_code>/stats`
Get click stats for a URL.

**Response `200`**
```json
{"short_code": "MQPKPq", "clicks": 42, "is_active": true}
```

---

## Events

### `GET /events`
List events. Supports filtering.

**Query params:** `page`, `per_page`, `url_id`, `user_id`, `event_type`

**Response `200`**
```json
[{"id": 1, "url_id": 1, "user_id": 1, "event_type": "created", "timestamp": "...", "details": {...}}]
```

### `GET /events/<id>`
Get event by ID.

**Response `200` / `404`**

### `POST /events`
Create an event manually.

**Body**
```json
{"url_id": 1, "user_id": 1, "event_type": "click", "details": {"referrer": "https://google.com"}}
```
`user_id` is optional.

**Response `201` / `400` / `404`**

---

## Error Responses

All errors return JSON:
```json
{"error": "Description of the problem"}
```

| Code | Meaning |
|------|---------|
| 400 | Bad request / invalid input |
| 404 | Resource not found |
| 405 | Method not allowed |
| 500 | Internal server error |
