"""Simulated Dynatrace tool for AMS agents."""
import random
from datetime import datetime, timedelta
from typing import Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


SIMULATED_SERVICES = [
    "payment-service", "auth-service", "inventory-service",
    "order-service", "notification-service", "api-gateway",
    "user-service", "recommendation-service"
]

ANOMALY_PATTERNS = {
    "payment-service": {
        "error_rate": 8.5,
        "avg_latency_ms": 2300,
        "p99_latency_ms": 8900,
        "throughput_rps": 142,
        "cpu_percent": 87,
        "memory_percent": 91,
        "anomalies": [
            "Database connection pool exhaustion detected",
            "Response time degradation > 3x baseline",
            "Error rate spike: 8.5% (threshold: 1%)"
        ]
    },
    "auth-service": {
        "error_rate": 0.2,
        "avg_latency_ms": 45,
        "p99_latency_ms": 120,
        "throughput_rps": 890,
        "cpu_percent": 23,
        "memory_percent": 41,
        "anomalies": []
    },
    "api-gateway": {
        "error_rate": 3.1,
        "avg_latency_ms": 890,
        "p99_latency_ms": 3200,
        "throughput_rps": 1240,
        "cpu_percent": 72,
        "memory_percent": 68,
        "anomalies": [
            "Upstream timeout cascade from payment-service",
            "Connection queue depth: 2847 (limit: 1000)"
        ]
    }
}


class DynatraceAnomalyInput(BaseModel):
    service_name: str = Field(description="Name of the service to check for anomalies")
    time_range_minutes: int = Field(default=30, description="Time range in minutes to analyze")


class DynatraceAnomalyTool(BaseTool):
    name: str = "dynatrace_get_anomalies"
    description: str = (
        "Fetches anomalies and performance signals from Dynatrace for a specific service. "
        "Returns error rates, latency metrics, CPU/memory usage, and detected anomalies."
    )
    args_schema: type[BaseModel] = DynatraceAnomalyInput

    def _run(self, service_name: str, time_range_minutes: int = 30) -> str:
        """Simulate Dynatrace anomaly detection API call."""
        if service_name in ANOMALY_PATTERNS:
            data = ANOMALY_PATTERNS[service_name]
        else:
            data = {
                "error_rate": round(random.uniform(0.1, 0.5), 2),
                "avg_latency_ms": random.randint(20, 100),
                "p99_latency_ms": random.randint(50, 300),
                "throughput_rps": random.randint(100, 2000),
                "cpu_percent": random.randint(10, 40),
                "memory_percent": random.randint(20, 60),
                "anomalies": []
            }

        timestamp = datetime.utcnow().isoformat()
        result = f"""
=== DYNATRACE ANOMALY REPORT ===
Service: {service_name}
Time Range: Last {time_range_minutes} minutes
Timestamp: {timestamp}

PERFORMANCE METRICS:
  Error Rate: {data['error_rate']}% (threshold: 1%)
  Avg Latency: {data['avg_latency_ms']}ms (baseline: 250ms)
  P99 Latency: {data['p99_latency_ms']}ms (SLO: 2000ms)
  Throughput: {data['throughput_rps']} RPS
  CPU Usage: {data['cpu_percent']}%
  Memory Usage: {data['memory_percent']}%

DETECTED ANOMALIES:
"""
        if data['anomalies']:
            for i, anomaly in enumerate(data['anomalies'], 1):
                result += f"  [{i}] {anomaly}\n"
        else:
            result += "  No anomalies detected - service operating normally\n"

        return result.strip()


class DynatraceTracingInput(BaseModel):
    trace_id: str = Field(description="Distributed trace ID to analyze")


class DynatraceTracingTool(BaseTool):
    name: str = "dynatrace_get_traces"
    description: str = (
        "Fetches distributed traces from Dynatrace to identify slow spans, "
        "failed operations, and dependency chain issues."
    )
    args_schema: type[BaseModel] = DynatraceTracingInput

    def _run(self, trace_id: str) -> str:
        """Simulate Dynatrace distributed tracing API call."""
        return f"""
=== DYNATRACE DISTRIBUTED TRACE ===
Trace ID: {trace_id}
Total Duration: 8,432ms (P99 baseline: 850ms)

SPAN BREAKDOWN:
  api-gateway [HTTP POST /api/payment]  ...... 8,432ms [ROOT]
  ├── auth-service [validate-token]  ......... 42ms    [OK]
  ├── payment-service [process-payment]  ..... 8,201ms [SLOW]
  │   ├── payment-db [connection-acquire]  ... 7,890ms [BOTTLENECK ⚠]
  │   │   └── connection-pool-wait  ........... 7,850ms [EXHAUSTED]
  │   └── fraud-check-service [validate]  .... 298ms   [OK]
  └── notification-service [send-confirm]  ... 189ms   [OK]

ROOT CAUSE INDICATORS:
  - Database connection pool exhausted (0/50 available)
  - Connection wait time: 7,850ms (timeout: 8,000ms)
  - Pool exhaustion started at: {(datetime.utcnow() - timedelta(minutes=23)).isoformat()}

AFFECTED ENDPOINTS:
  - POST /api/payment (error_rate: 8.5%, affected: 847 requests)
  - GET /api/payment/status (timeout: 100%, affected: 1,203 requests)
        """.strip()


class DynatraceTopologyInput(BaseModel):
    service_name: str = Field(description="Service to get dependency topology for")


class DynatraceTopologyTool(BaseTool):
    name: str = "dynatrace_get_topology"
    description: str = (
        "Gets the service dependency topology and impact analysis from Dynatrace. "
        "Shows which services are affected by a given service's degradation."
    )
    args_schema: type[BaseModel] = DynatraceTopologyInput

    def _run(self, service_name: str) -> str:
        """Simulate Dynatrace topology/smartscape API call."""
        return f"""
=== DYNATRACE TOPOLOGY & IMPACT MAP ===
Service: {service_name}
Analysis Timestamp: {datetime.utcnow().isoformat()}

UPSTREAM DEPENDENTS (impacted by {service_name} degradation):
  api-gateway ────────► {service_name} [CRITICAL DEPENDENCY]
    ├── mobile-app (1.2M active users)
    ├── web-frontend (890K active sessions)
    └── partner-api (47 enterprise integrations)

DOWNSTREAM DEPENDENCIES ({service_name} depends on):
  {service_name} ────► payment-db (PostgreSQL 14.8)
    └── primary-replica (read/write, connection_pool: 50)
  {service_name} ────► fraud-check-service [healthy]
  {service_name} ────► payment-vault (secrets) [healthy]

BLAST RADIUS:
  Directly Impacted Services: 3
  Transitively Impacted: 8
  Affected User Sessions: ~2.1M
  Estimated Revenue Impact: $12,400/minute
        """.strip()
