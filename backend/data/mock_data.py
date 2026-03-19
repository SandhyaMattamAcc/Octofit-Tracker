"""Mock data generator for dashboard demo without LLM API calls."""
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any


def generate_incidents() -> List[Dict]:
    """Generate realistic mock incidents for dashboard display."""
    now = datetime.utcnow()
    return [
        {
            "id": "INC0012847",
            "title": "Payment Service Critical Degradation",
            "severity": "critical",
            "status": "in_progress",
            "affected_services": ["payment-service", "api-gateway", "order-service"],
            "business_impact": "~$12,400/min revenue impact, 2.1M users affected",
            "business_impact_score": 95,
            "root_cause": "Database connection pool exhaustion (0/50 available) causing cascade timeout",
            "remediation_actions": [
                "✅ AUTO: Reset connection pool (LOW risk) - Executed",
                "✅ AUTO: Scale payment-service to 8 replicas (MEDIUM risk) - Executed",
                "⏳ PENDING APPROVAL: Increase DB max_connections to 200 (HIGH risk)",
            ],
            "validation_results": "Error rate recovering: 8.5% → 2.1%. Awaiting human approval for DB change.",
            "created_at": (now - timedelta(minutes=34)).isoformat(),
            "updated_at": (now - timedelta(minutes=2)).isoformat(),
            "mttr_minutes": None,
            "assigned_to": "SRE-Team-Alpha",
            "agent_phase": "remediation",
        },
        {
            "id": "INC0012831",
            "title": "Auth Service Latency Spike",
            "severity": "high",
            "status": "resolved",
            "affected_services": ["auth-service", "user-service"],
            "business_impact": "$2,100/min impact, 340K users affected during peak",
            "business_impact_score": 72,
            "root_cause": "Memory leak in JWT validation cache causing GC pressure",
            "remediation_actions": [
                "✅ AUTO: Rolling restart of auth-service pods (LOW risk) - Executed",
                "✅ AUTO: Cleared JWT cache (LOW risk) - Executed",
            ],
            "validation_results": "✅ GO: All SLOs recovered. P99 latency: 45ms (SLO: 200ms). Error budget stable.",
            "created_at": (now - timedelta(hours=3, minutes=12)).isoformat(),
            "updated_at": (now - timedelta(hours=2, minutes=8)).isoformat(),
            "mttr_minutes": 64,
            "assigned_to": "SRE-Team-Beta",
            "agent_phase": "completed",
        },
        {
            "id": "INC0012819",
            "title": "Recommendation Engine Timeout",
            "severity": "medium",
            "status": "resolved",
            "affected_services": ["recommendation-service"],
            "business_impact": "$890/min impact, degraded UX for 1.2M users",
            "business_impact_score": 43,
            "root_cause": "ML model inference timeout due to unoptimized feature vector computation",
            "remediation_actions": [
                "✅ AUTO: Increased timeout threshold (LOW risk) - Executed",
                "✅ AUTO: Enabled fallback to cached recommendations (LOW risk) - Executed",
            ],
            "validation_results": "✅ GO: Service restored. Fallback performing well. Permanent fix scheduled.",
            "created_at": (now - timedelta(hours=8, minutes=45)).isoformat(),
            "updated_at": (now - timedelta(hours=7, minutes=30)).isoformat(),
            "mttr_minutes": 75,
            "assigned_to": "SRE-Team-Alpha",
            "agent_phase": "completed",
        },
    ]


def generate_signals() -> List[Dict]:
    """Generate mock observability signals."""
    now = datetime.utcnow()
    return [
        {
            "id": "SIG-001",
            "source": "dynatrace",
            "type": "error_rate",
            "service": "payment-service",
            "severity": "critical",
            "value": 8.5,
            "threshold": 1.0,
            "timestamp": (now - timedelta(minutes=34)).isoformat(),
            "correlated_signals": ["SIG-002", "SIG-003"],
            "metadata": {"unit": "%", "baseline": 0.3}
        },
        {
            "id": "SIG-002",
            "source": "dynatrace",
            "type": "latency",
            "service": "payment-service",
            "severity": "critical",
            "value": 8432,
            "threshold": 2000,
            "timestamp": (now - timedelta(minutes=33)).isoformat(),
            "correlated_signals": ["SIG-001"],
            "metadata": {"unit": "ms", "baseline": 245}
        },
        {
            "id": "SIG-003",
            "source": "dynatrace",
            "type": "connection_pool",
            "service": "payment-db",
            "severity": "critical",
            "value": 0,
            "threshold": 10,
            "timestamp": (now - timedelta(minutes=35)).isoformat(),
            "correlated_signals": ["SIG-001", "SIG-002"],
            "metadata": {"unit": "connections", "max_pool": 50}
        },
        {
            "id": "SIG-004",
            "source": "dynatrace",
            "type": "error_rate",
            "service": "api-gateway",
            "severity": "high",
            "value": 3.1,
            "threshold": 1.0,
            "timestamp": (now - timedelta(minutes=32)).isoformat(),
            "correlated_signals": ["SIG-001"],
            "metadata": {"unit": "%", "cause": "upstream timeout cascade"}
        },
    ]


def generate_service_health() -> List[Dict]:
    """Generate service health metrics."""
    services = [
        {
            "service": "payment-service",
            "status": "degraded",
            "availability": 91.5,
            "error_rate": 8.5,
            "avg_latency_ms": 2300,
            "p99_latency_ms": 8900,
            "throughput_rps": 142,
            "apdex_score": 0.42,
        },
        {
            "service": "auth-service",
            "status": "healthy",
            "availability": 99.98,
            "error_rate": 0.02,
            "avg_latency_ms": 45,
            "p99_latency_ms": 120,
            "throughput_rps": 890,
            "apdex_score": 0.98,
        },
        {
            "service": "api-gateway",
            "status": "degraded",
            "availability": 96.9,
            "error_rate": 3.1,
            "avg_latency_ms": 890,
            "p99_latency_ms": 3200,
            "throughput_rps": 1240,
            "apdex_score": 0.71,
        },
        {
            "service": "order-service",
            "status": "healthy",
            "availability": 99.87,
            "error_rate": 0.13,
            "avg_latency_ms": 180,
            "p99_latency_ms": 450,
            "throughput_rps": 320,
            "apdex_score": 0.95,
        },
        {
            "service": "inventory-service",
            "status": "healthy",
            "availability": 99.95,
            "error_rate": 0.05,
            "avg_latency_ms": 65,
            "p99_latency_ms": 180,
            "throughput_rps": 780,
            "apdex_score": 0.99,
        },
        {
            "service": "notification-service",
            "status": "healthy",
            "availability": 99.91,
            "error_rate": 0.09,
            "avg_latency_ms": 95,
            "p99_latency_ms": 280,
            "throughput_rps": 450,
            "apdex_score": 0.97,
        },
    ]
    return services


def generate_business_metrics() -> Dict:
    """Generate executive business metrics."""
    return {
        "revenue_impact_per_hour": 744000,
        "affected_users": 2100000,
        "transaction_success_rate": 91.5,
        "sla_compliance": 96.8,
        "open_incidents": 1,
        "critical_incidents": 1,
        "mttr_avg_minutes": 69.5,
        "recurrence_rate": 12.3,
        "incidents_last_30_days": 23,
        "auto_resolved_percent": 61,
        "cost_avoided_usd": 2840000,
        "revenue_at_risk_usd": 744000,
    }


def generate_sre_metrics() -> Dict:
    """Generate SRE-specific metrics."""
    return {
        "slo_compliance": {
            "payment-service": 91.5,
            "auth-service": 99.98,
            "api-gateway": 96.9,
            "order-service": 99.87,
            "overall": 97.1,
        },
        "error_budget_remaining": {
            "payment-service": -32.5,  # negative = over budget
            "auth-service": 94.2,
            "api-gateway": 68.1,
            "order-service": 88.7,
            "overall": 54.6,
        },
        "change_failure_rate": 4.2,
        "deployment_frequency": 12.3,
        "lead_time_hours": 2.4,
        "alert_fatigue_score": 34,
        "false_positive_rate": 8.7,
        "mean_time_to_detect_minutes": 4.2,
        "mean_time_to_resolve_minutes": 69.5,
    }


def generate_agent_pipeline_state(incident_id: str = "INC0012847") -> List[Dict]:
    """Generate mock agent pipeline state for the active incident."""
    now = datetime.utcnow()
    return [
        {
            "agent_name": "Signal Detection & Correlation",
            "task_description": "Detect and correlate anomaly signals across payment-service and downstream",
            "status": "completed",
            "result": (
                "CORRELATION REPORT: Primary anomaly in payment-db (connection pool exhaustion). "
                "Cascading to payment-service (8.5% errors) → api-gateway (3.1% errors). "
                "Blast radius: 3 services, 2.1M users. Severity: CRITICAL (confidence: 96%)"
            ),
            "started_at": (now - timedelta(minutes=33)).isoformat(),
            "completed_at": (now - timedelta(minutes=30)).isoformat(),
            "requires_approval": False,
            "icon": "🔍",
        },
        {
            "agent_name": "Business Impact Analyzer",
            "task_description": "Quantify revenue, SLA, and user impact of the incident",
            "status": "completed",
            "result": (
                "IMPACT REPORT: Revenue impact $12,400/min ($744K/hr). 2.1M active users affected. "
                "SLA P1 breach in 23 min if unresolved. Business impact score: 95/100. "
                "Partner API integrations at risk: 47 enterprises."
            ),
            "started_at": (now - timedelta(minutes=30)).isoformat(),
            "completed_at": (now - timedelta(minutes=27)).isoformat(),
            "requires_approval": False,
            "icon": "📊",
        },
        {
            "agent_name": "Root Cause Analyzer",
            "task_description": "Identify definitive root cause via distributed trace analysis",
            "status": "completed",
            "result": (
                "ROOT CAUSE: Database connection pool exhaustion (0/50 connections available). "
                "Triggered by long-running transaction from payment-service v2.4.1 (deployed 2h ago). "
                "Evidence: 7,850ms pool wait time in traces. Pattern: Known (KB0004521, 3rd occurrence). "
                "Confidence: 97%"
            ),
            "started_at": (now - timedelta(minutes=27)).isoformat(),
            "completed_at": (now - timedelta(minutes=22)).isoformat(),
            "requires_approval": False,
            "icon": "🔬",
        },
        {
            "agent_name": "Safe Remediation Executor",
            "task_description": "Execute safe remediation with guardrails and human-in-the-loop",
            "status": "completed",
            "result": (
                "REMEDIATION EXECUTED:\n"
                "✅ LOW RISK (auto): Connection pool reset → DONE (error rate: 8.5% → 4.2%)\n"
                "✅ MEDIUM RISK (auto): Scale to 8 replicas → DONE (error rate: 4.2% → 2.1%)\n"
                "⏳ HIGH RISK (awaiting approval): Increase DB max_connections 100→200\n"
                "Rollback plan documented. MTTR so far: 12 minutes."
            ),
            "started_at": (now - timedelta(minutes=22)).isoformat(),
            "completed_at": (now - timedelta(minutes=15)).isoformat(),
            "requires_approval": True,
            "icon": "⚡",
        },
        {
            "agent_name": "SRE Signal Validator",
            "task_description": "Validate remediation success via SLO/SLI recovery signals",
            "status": "completed",
            "result": (
                "VALIDATION: Partial recovery detected.\n"
                "✅ Error rate: 8.5% → 2.1% (target <1%)\n"
                "⚠️ P99 Latency: 8,432ms → 3,200ms (target <2,000ms)\n"
                "⚠️ Connection pool: 0 → 23/50 (recovering)\n"
                "⏳ NO-GO: DB max_connections change pending approval. Continue monitoring."
            ),
            "started_at": (now - timedelta(minutes=15)).isoformat(),
            "completed_at": (now - timedelta(minutes=8)).isoformat(),
            "requires_approval": False,
            "icon": "✅",
        },
        {
            "agent_name": "Knowledge Updater",
            "task_description": "Update knowledge base and create prevention plan",
            "status": "running",
            "result": None,
            "started_at": (now - timedelta(minutes=8)).isoformat(),
            "completed_at": None,
            "requires_approval": False,
            "icon": "📚",
        },
    ]


def generate_knowledge_articles() -> List[Dict]:
    """Generate mock knowledge articles."""
    now = datetime.utcnow()
    return [
        {
            "id": "KB0004521",
            "incident_id": "INC0012819",
            "title": "Payment DB Connection Pool Exhaustion - Detection & Resolution",
            "root_cause_pattern": "Long-running DB transactions exhausting connection pool (< 5 connections available)",
            "prevention_steps": [
                "Alert: connection_pool_usage > 80% for 2 minutes",
                "Auto-remediation: Increase pool size when > 90% for 1 minute",
                "Code review checklist: Verify connection release in finally blocks",
                "Deployment gate: Require load test showing pool usage < 60% at peak",
            ],
            "automation_runbook": "runbook://payment-db-pool-exhaustion-v3",
            "confidence_score": 0.97,
            "created_at": (now - timedelta(days=45)).isoformat(),
            "occurrences": 3,
        },
        {
            "id": "KB0003891",
            "incident_id": "INC0012831",
            "title": "API Gateway Upstream Cascade Timeout Pattern",
            "root_cause_pattern": "Upstream service degradation exceeding gateway timeout causing connection queue overflow",
            "prevention_steps": [
                "Configure circuit breaker: 50% error rate threshold, 30s window",
                "Bulkhead pattern: Separate thread pools per upstream service",
                "Adaptive timeout: Reduce timeout when upstream P99 > 2x baseline",
                "Canary alerting: Detect upstream degradation within 30 seconds",
            ],
            "automation_runbook": "runbook://api-gateway-circuit-breaker-activation",
            "confidence_score": 0.91,
            "created_at": (now - timedelta(days=12)).isoformat(),
            "occurrences": 7,
        },
    ]
