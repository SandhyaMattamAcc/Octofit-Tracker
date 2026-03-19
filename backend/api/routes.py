"""FastAPI routes for the AMS Dashboard API."""
import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from backend.models.schemas import ApprovalRequest
from backend.data.mock_data import (
    generate_incidents, generate_signals, generate_service_health,
    generate_business_metrics, generate_sre_metrics,
    generate_agent_pipeline_state, generate_knowledge_articles
)

router = APIRouter(prefix="/api/v1", tags=["AMS Dashboard"])

# In-memory store for active crew runs
active_runs: Dict[str, Dict] = {}
incident_store = {inc["id"]: inc for inc in generate_incidents()}


# ─── Dashboard Data Endpoints ──────────────────────────────────────────────────

@router.get("/dashboard/executive")
async def get_executive_dashboard():
    """Executive view: high-level business metrics and incident summary."""
    incidents = list(incident_store.values())
    business = generate_business_metrics()
    services = generate_service_health()

    critical = [i for i in incidents if i["severity"] == "critical" and i["status"] != "resolved"]
    resolved_with_mttr = [i for i in incidents if i.get("mttr_minutes")]

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "business_metrics": business,
        "active_critical_incidents": critical,
        "services_summary": {
            "total": len(services),
            "healthy": sum(1 for s in services if s["status"] == "healthy"),
            "degraded": sum(1 for s in services if s["status"] == "degraded"),
            "down": sum(1 for s in services if s["status"] == "down"),
        },
        "mttr_trend": {
            "current_avg_minutes": business["mttr_avg_minutes"],
            "previous_avg_minutes": 142.0,
            "improvement_percent": 51.1,
        },
        "automation_roi": {
            "incidents_auto_resolved": business["auto_resolved_percent"],
            "cost_avoided_usd": business["cost_avoided_usd"],
            "engineer_hours_saved": 847,
        },
    }


@router.get("/dashboard/ops")
async def get_ops_dashboard():
    """Ops view: incident queue, service health, agent pipeline status."""
    incidents = list(incident_store.values())
    services = generate_service_health()
    signals = generate_signals()

    active_incident = next((i for i in incidents if i["status"] == "in_progress"), None)
    agent_pipeline = generate_agent_pipeline_state(
        active_incident["id"] if active_incident else "INC0012847"
    )

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "incident_queue": sorted(
            incidents,
            key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x["severity"]]
        ),
        "service_health": services,
        "active_signals": signals,
        "agent_pipeline": {
            "incident_id": active_incident["id"] if active_incident else None,
            "phases": agent_pipeline,
            "human_approval_pending": any(
                p["requires_approval"] and p["status"] == "completed"
                for p in agent_pipeline
            ),
            "overall_status": "running" if active_incident else "idle",
        },
        "ops_summary": {
            "open_incidents": sum(1 for i in incidents if i["status"] != "resolved"),
            "pending_approvals": 1,
            "auto_actions_today": 14,
            "signals_processed_today": 847,
        },
    }


@router.get("/dashboard/sre")
async def get_sre_dashboard():
    """SRE view: SLOs, error budgets, reliability metrics, and agent validation."""
    sre_metrics = generate_sre_metrics()
    services = generate_service_health()
    knowledge = generate_knowledge_articles()
    incidents = list(incident_store.values())

    active_incident = next((i for i in incidents if i["status"] == "in_progress"), None)
    agent_pipeline = generate_agent_pipeline_state(
        active_incident["id"] if active_incident else "INC0012847"
    )

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sre_metrics": sre_metrics,
        "service_reliability": services,
        "slo_details": [
            {
                "service": service,
                "slo_target": 99.9,
                "current_compliance": compliance,
                "error_budget_remaining": sre_metrics["error_budget_remaining"].get(service, 100),
                "status": "ok" if compliance >= 99.0 else "warning" if compliance >= 97.0 else "breach",
            }
            for service, compliance in sre_metrics["slo_compliance"].items()
            if service != "overall"
        ],
        "validation_pipeline": agent_pipeline,
        "knowledge_base": knowledge,
        "reliability_trends": {
            "mttr_minutes": sre_metrics["mean_time_to_resolve_minutes"],
            "mttd_minutes": sre_metrics["mean_time_to_detect_minutes"],
            "alert_fatigue_score": sre_metrics["alert_fatigue_score"],
            "false_positive_rate": sre_metrics["false_positive_rate"],
        },
    }


# ─── Incident Endpoints ─────────────────────────────────────────────────────────

@router.get("/incidents")
async def list_incidents(severity: Optional[str] = None, status: Optional[str] = None):
    """List all incidents with optional filtering."""
    incidents = list(incident_store.values())
    if severity:
        incidents = [i for i in incidents if i["severity"] == severity]
    if status:
        incidents = [i for i in incidents if i["status"] == status]
    return {"incidents": incidents, "total": len(incidents)}


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get a specific incident with full details."""
    if incident_id not in incident_store:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    incident = incident_store[incident_id]
    pipeline = generate_agent_pipeline_state(incident_id)
    return {"incident": incident, "agent_pipeline": pipeline}


# ─── Agent Control Endpoints ───────────────────────────────────────────────────

@router.post("/agents/run")
async def trigger_agent_run(
    background_tasks: BackgroundTasks,
    service_name: str = "payment-service",
    incident_id: Optional[str] = None,
    initial_signals: str = "High error rate and latency detected",
):
    """Trigger the AMS agent crew to process an incident.

    Note: In production this runs the full CrewAI pipeline.
    In demo mode, returns simulated pipeline state.
    """
    if not incident_id:
        incident_id = f"INC{uuid.uuid4().int % 9999999:07d}"

    run_id = str(uuid.uuid4())[:8]
    run_state = {
        "run_id": run_id,
        "incident_id": incident_id,
        "service_name": service_name,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "demo_mode": True,
        "message": (
            "Agent crew initiated. In production, this triggers the full CrewAI pipeline. "
            "Set OPENAI_API_KEY to enable live agent execution."
        )
    }

    active_runs[run_id] = run_state
    return run_state


@router.get("/agents/runs/{run_id}")
async def get_run_status(run_id: str):
    """Get the status of an active or completed agent run."""
    if run_id in active_runs:
        return active_runs[run_id]
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found")


@router.get("/agents/pipeline/{incident_id}")
async def get_agent_pipeline(incident_id: str):
    """Get the current agent pipeline state for an incident."""
    pipeline = generate_agent_pipeline_state(incident_id)
    return {
        "incident_id": incident_id,
        "pipeline": pipeline,
        "completed_phases": sum(1 for p in pipeline if p["status"] == "completed"),
        "total_phases": len(pipeline),
        "human_approval_pending": any(
            p["requires_approval"] and p["status"] == "completed" for p in pipeline
        ),
    }


@router.post("/agents/approve")
async def approve_remediation(request: ApprovalRequest):
    """Human-in-the-loop approval for high-risk remediation actions."""
    if request.incident_id not in incident_store:
        raise HTTPException(status_code=404, detail=f"Incident {request.incident_id} not found")

    incident = incident_store[request.incident_id]

    if request.approved:
        # Update the incident to reflect approval
        incident["remediation_actions"] = [
            action.replace("⏳ PENDING APPROVAL:", "✅ APPROVED:")
            for action in incident.get("remediation_actions", [])
        ]
        incident["updated_at"] = datetime.utcnow().isoformat()
        message = f"Remediation approved by {request.approver}. Executing high-risk actions."
    else:
        incident["updated_at"] = datetime.utcnow().isoformat()
        message = f"Remediation rejected by {request.approver}. High-risk actions cancelled."

    return {
        "incident_id": request.incident_id,
        "approved": request.approved,
        "approver": request.approver,
        "timestamp": datetime.utcnow().isoformat(),
        "message": message,
        "incident": incident,
    }


# ─── Service & Signal Endpoints ────────────────────────────────────────────────

@router.get("/services/health")
async def get_service_health():
    """Get health status of all monitored services."""
    return {"services": generate_service_health()}


@router.get("/signals")
async def get_signals(service: Optional[str] = None):
    """Get active observability signals."""
    signals = generate_signals()
    if service:
        signals = [s for s in signals if s["service"] == service]
    return {"signals": signals, "total": len(signals)}


@router.get("/knowledge")
async def get_knowledge_articles():
    """Get knowledge base articles from resolved incidents."""
    return {"articles": generate_knowledge_articles()}
