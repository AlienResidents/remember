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

USER_COUNT = Gauge(
    "remember_users_total",
    "Total number of users",
    ["provider"],
)

# Tool metrics
TOOL_CALL_COUNT = Counter(
    "remember_tools_calls_total",
    "Total number of tool calls",
    ["tool_name"],
)

TOOL_CALL_DURATION = Histogram(
    "remember_tools_calls_duration_seconds",
    "Tool call duration in seconds",
    ["tool_name"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)


def start_metrics_server(port: int = 9090):
    """Start the Prometheus metrics HTTP server.

    Args:
        port: Port to listen on (default: 9090)
    """
    start_http_server(port)


def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record a request metric.

    Args:
        method: HTTP method
        endpoint: Endpoint path
        status: HTTP status code
        duration: Request duration in seconds
    """
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def record_tool_call(tool_name: str, duration: float):
    """Record a tool call metric.

    Args:
        tool_name: Name of the tool
        duration: Tool call duration in seconds
    """
    TOOL_CALL_COUNT.labels(tool_name=tool_name).inc()
    TOOL_CALL_DURATION.labels(tool_name=tool_name).observe(duration)
