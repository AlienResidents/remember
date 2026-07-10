"""Tests for metrics."""

import pytest

pytest.importorskip("prometheus_client")

from remember.metrics import (
    record_request,
    record_tool_call,
    REQUEST_COUNT,
    TOOL_CALL_COUNT,
)


def test_record_request():
    """Test recording a request."""
    # Should not raise
    record_request("GET", "/healthz", 200, 0.01)


def test_record_tool_call():
    """Test recording a tool call."""
    # Should not raise
    record_tool_call("search_memories", 0.05)


def test_metrics_counters_increment():
    """Test that counters increment."""
    initial = REQUEST_COUNT.labels(method="GET", endpoint="/test", status="200")._value.get()
    record_request("GET", "/test", 200, 0.01)
    after = REQUEST_COUNT.labels(method="GET", endpoint="/test", status="200")._value.get()
    assert after == initial + 1
