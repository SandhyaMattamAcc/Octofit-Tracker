"""Pydantic schemas for AMS dashboard data models."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"


class Signal(BaseModel):
    id: str
    source: str  # dynatrace, prometheus, logs, etc.
    type: str    # anomaly, threshold, error_rate, latency
    service: str
    severity: Severity
    value: float
    threshold: float
    timestamp: datetime
    correlated_signals: List[str] = []
    metadata: Dict[str, Any] = {}


class Incident(BaseModel):
    id: str
    title: str
    severity: Severity
    status: IncidentStatus
    affected_services: List[str]
    signals: List[Signal] = []
    business_impact: Optional[str] = None
    business_impact_score: Optional[float] = None
    root_cause: Optional[str] = None
    remediation_actions: List[str] = []
    validation_results: Optional[str] = None
    knowledge_article: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    mttr_minutes: Optional[int] = None
    assigned_to: Optional[str] = None


class AgentTask(BaseModel):
    agent_name: str
    task_description: str
    status: AgentStatus
    result: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    requires_approval: bool = False


class CrewRun(BaseModel):
    id: str
    incident_id: str
    status: AgentStatus
    agents: List[AgentTask] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    human_approval_pending: bool = False
    approval_context: Optional[str] = None


class ServiceHealth(BaseModel):
    service: str
    status: str  # healthy, degraded, down
    availability: float  # percentage
    error_rate: float
    avg_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    apdex_score: float


class BusinessMetrics(BaseModel):
    revenue_impact_per_hour: float
    affected_users: int
    transaction_success_rate: float
    sla_compliance: float
    open_incidents: int
    critical_incidents: int
    mttr_avg_minutes: float
    recurrence_rate: float


class SREMetrics(BaseModel):
    slo_compliance: Dict[str, float]
    error_budget_remaining: Dict[str, float]
    change_failure_rate: float
    deployment_frequency: float
    lead_time_hours: float
    alert_fatigue_score: float
    false_positive_rate: float


class KnowledgeArticle(BaseModel):
    id: str
    incident_id: str
    title: str
    root_cause_pattern: str
    prevention_steps: List[str]
    automation_runbook: Optional[str] = None
    confidence_score: float
    created_at: datetime


class RemediationAction(BaseModel):
    id: str
    action_type: str  # restart, scale, rollback, config_change
    target_service: str
    description: str
    risk_level: str  # low, medium, high
    requires_approval: bool
    automated: bool
    rollback_plan: str


class ApprovalRequest(BaseModel):
    incident_id: str
    action: str
    approved: bool
    approver: str = "SRE-Lead"
