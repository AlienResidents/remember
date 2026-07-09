---
type: Source Code
description: "Prometheus metrics for REMEMBER server."
resource: server/remember/metrics.py
timestamp: 2026-07-09T13:05:53Z
---

# metrics

Source path: `server/remember/metrics.py`

## Content

```python
"""Prometheus metrics for REMEMBER server."""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    start_http_server,
)

# Request metrics
REQUEST_COUNT = Counter(
    "remember_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "remember_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Database metrics
DB_CONNECTIONS_ACTIVE = Gauge(
    "remember_db_connections_active",
    "Active database connections",
)

DB_CONNECTIONS_IDLE = Gauge(
    "remember_db_connections_idle",
    "Idle database connections",
)

# Memory metrics
MEMORY_COUNT = Gauge(
    "remember_memories_total",
    "Total number of memories",
    ["type", "status"],
)
```

*…truncated — full source at `server/remember/metrics.py`*
