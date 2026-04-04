accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '{"time": "%(t)s", "level": "INFO", "logger": "gunicorn.access", "method": "%(m)s", "path": "%(U)s", "status": %(s)s, "duration_ms": %(D)s}'
