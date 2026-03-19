"""Hierarchical AMS Crew orchestration using CrewAI."""
import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from crewai import Crew, Task, Process

from backend.agents import (
    create_signal_detector_agent,
    create_impact_analyzer_agent,
    create_root_cause_analyzer_agent,
    create_remediation_executor_agent,
    create_sre_validator_agent,
    create_knowledge_updater_agent,
)


def create_ams_tasks(
    incident_id: str,
    service_name: str,
    initial_signals: str,
    agents: Dict[str, Any],
) -> list:
    """Create the sequential task pipeline for AMS incident processing."""

    signal_detection_task = Task(
        description=f"""
        INCIDENT: {incident_id}
        PRIMARY SERVICE: {service_name}
        INITIAL SIGNALS: {initial_signals}

        Your mission: Detect and correlate ALL signals related to this incident.

        1. Use dynatrace_get_anomalies to analyze {service_name} for the last 30 minutes
        2. Use dynatrace_get_traces to analyze trace ID: TRACE-{incident_id[:8]} for span-level bottlenecks
        3. Use dynatrace_get_topology to map the full blast radius from {service_name}
        4. Correlate all findings to identify:
           - Which signals are root causes vs cascading effects
           - The full scope of affected services
           - Severity classification based on combined signal strength
           - Confidence score for your correlation

        Output a structured Signal Correlation Report with:
        - Primary anomaly source
        - Correlated signals list (cause → effect chain)
        - Blast radius summary
        - Recommended severity level
        """,
        expected_output=(
            "A comprehensive Signal Correlation Report containing: primary anomaly identification, "
            "correlated signal chain showing cause-and-effect relationships, full blast radius with "
            "all affected services, severity assessment (Critical/High/Medium/Low) with justification, "
            "and confidence score (0-100%)."
        ),
        agent=agents["signal_detector"],
    )

    impact_analysis_task = Task(
        description=f"""
        Using the Signal Correlation Report from the previous analysis of incident {incident_id}:

        1. Use dynatrace_get_topology to get the business service topology for {service_name}
        2. Use servicenow_get_incident to retrieve ITSM context for {incident_id}
        3. Use servicenow_search_knowledge to find similar past incidents and their business impact

        Calculate and report:
        - Revenue impact per minute/hour (use topology data: ~$12,400/minute)
        - Number of affected end users (from topology data)
        - Which SLA/SLO commitments are at risk or already breached
        - Business service impact score (0-100)
        - Executive summary (3 sentences max) suitable for C-suite briefing
        - Estimated time-to-business-recovery if incident continues unresolved

        IMPORTANT: Quantify everything with numbers. No vague statements.
        """,
        expected_output=(
            "A Business Impact Report containing: revenue loss calculation ($/minute and projected $/hour), "
            "affected user count, SLA breach risk assessment, business impact score (0-100), "
            "executive summary (3 sentences), and time-to-recovery projection."
        ),
        agent=agents["impact_analyzer"],
        context=[signal_detection_task],
    )

    root_cause_task = Task(
        description=f"""
        Using the Signal Correlation Report and Business Impact Report for incident {incident_id}:

        Perform definitive Root Cause Analysis:

        1. Use dynatrace_get_traces with trace ID: TRACE-{incident_id[:8]} to analyze the exact failure point
        2. Use dynatrace_get_anomalies for {service_name} to identify metric deviations
        3. Use servicenow_search_knowledge with query: "database connection pool exhaustion payment service"
           to check for known patterns
        4. Apply fault tree analysis:
           - Top event: What failed?
           - Intermediate events: What caused the failure?
           - Basic events: What is the underlying root cause?
        5. Cross-reference with knowledge base to determine if this is recurring

        Produce:
        - Definitive root cause statement (1-2 sentences, specific and actionable)
        - Evidence chain (each piece of evidence supporting the root cause)
        - Confidence level (0-100%) with justification
        - Recurrence risk assessment (is this pattern seen before?)
        - Contributing factors (secondary causes)
        """,
        expected_output=(
            "A Root Cause Analysis Report containing: definitive root cause statement, evidence chain "
            "with 3+ supporting data points, confidence level percentage with justification, "
            "recurrence risk assessment (new/known pattern), and contributing factors list."
        ),
        agent=agents["root_cause_analyzer"],
        context=[signal_detection_task, impact_analysis_task],
    )

    remediation_task = Task(
        description=f"""
        Using the Root Cause Analysis for incident {incident_id}:

        Generate and execute safe remediation:

        1. Use servicenow_search_knowledge to find proven remediation procedures for the identified root cause
        2. Use dynatrace_get_anomalies to confirm current service state before acting
        3. Generate a prioritized remediation plan:

        RISK CLASSIFICATION RULES (MANDATORY):
        - LOW RISK (auto-execute): service restart, cache flush, connection pool reset, config reload
        - MEDIUM RISK (notify + auto-execute): horizontal scaling, traffic rerouting
        - HIGH RISK (REQUIRE HUMAN APPROVAL): database changes, deployment rollback, infrastructure changes

        For each action provide:
        - Action description
        - Risk level (LOW/MEDIUM/HIGH)
        - Whether it requires human approval
        - Rollback procedure
        - Expected recovery time

        4. Use servicenow_update_incident to document:
           - All planned actions
           - Auto-executed safe actions (simulate execution)
           - Human approval required actions (flag them clearly)

        GUARDRAILS:
        - Never execute HIGH risk actions without approval
        - Always document rollback before executing
        - If uncertain about risk level, escalate to HIGH
        """,
        expected_output=(
            "A Remediation Plan containing: ordered action list with risk classifications, "
            "auto-executed actions (LOW/MEDIUM risk) with confirmation, human-approval-required "
            "actions (HIGH risk) clearly flagged, rollback procedures for each action, "
            "ServiceNow ticket update confirmation, and expected MTTR."
        ),
        agent=agents["remediation_executor"],
        context=[root_cause_task],
    )

    validation_task = Task(
        description=f"""
        Validate remediation success for incident {incident_id}:

        1. Use dynatrace_get_anomalies for {service_name} to check post-remediation metrics
        2. Use dynatrace_get_traces with TRACE-{incident_id[:8]}-POST to verify trace improvement
        3. Use dynatrace_get_topology to verify cascade recovery across all affected services

        Validation Criteria (ALL must pass for GO signal):
        ✓ Error rate returned to baseline (< 1%)
        ✓ P99 latency within SLO (< 2000ms)
        ✓ Connection pool metrics normalized
        ✓ No new anomalies in downstream services
        ✓ SLO compliance restored

        Check:
        - SLO status: compliance percentage vs target
        - Error budget: burn rate recovery
        - Adjacent service health (no regressions)
        - Observation window: stable for minimum 5 minutes

        Provide:
        - GO/NO-GO decision with justification
        - Validation checklist with pass/fail for each criterion
        - Recommended observation window before full closure
        - Any residual risks or monitoring recommendations
        """,
        expected_output=(
            "A Validation Report containing: GO/NO-GO decision with clear justification, "
            "validation checklist (pass/fail for each criterion), SLO compliance status, "
            "error budget recovery assessment, residual risk summary, and recommended "
            "monitoring period before incident closure."
        ),
        agent=agents["sre_validator"],
        context=[remediation_task],
    )

    knowledge_update_task = Task(
        description=f"""
        Close the learning loop for incident {incident_id}:

        1. Use servicenow_search_knowledge to check if a knowledge article already exists for this pattern
        2. Use servicenow_create_problem to create a Problem record if this is a recurring issue:
           - Incident ID: {incident_id}
           - Problem statement: Based on the root cause findings
           - Root cause: From the RCA report
           - Prevention plan: Specific, actionable steps

        3. Use servicenow_update_incident to add final closure notes:
           - Complete RCA summary
           - Remediation actions taken
           - Validation results
           - Link to knowledge article
           - MTTR achieved

        4. Generate a Knowledge Article with:
           - Incident pattern description (for future detection)
           - Root cause (verified)
           - Resolution steps (proven to work)
           - Prevention measures (specific and actionable)
           - Automation opportunity assessment
           - Recurrence risk score (0-100)

        5. Propose specific automation improvements:
           - What monitoring alert would catch this earlier?
           - What auto-remediation could resolve this automatically next time?
           - What architectural change would prevent recurrence?
        """,
        expected_output=(
            "A Knowledge Update Report containing: ServiceNow Problem record number, "
            "knowledge article content (pattern, root cause, resolution, prevention), "
            "incident closure notes, automation improvement proposals (3+ specific items), "
            "recurrence risk score with trend analysis, and estimated MTTR reduction "
            "if automation is implemented."
        ),
        agent=agents["knowledge_updater"],
        context=[signal_detection_task, root_cause_task, validation_task],
    )

    return [
        signal_detection_task,
        impact_analysis_task,
        root_cause_task,
        remediation_task,
        validation_task,
        knowledge_update_task,
    ]


def build_ams_crew(
    incident_id: str,
    service_name: str,
    initial_signals: str,
    llm=None,
) -> Crew:
    """Build the hierarchical AMS crew for incident processing."""

    agents = {
        "signal_detector": create_signal_detector_agent(llm),
        "impact_analyzer": create_impact_analyzer_agent(llm),
        "root_cause_analyzer": create_root_cause_analyzer_agent(llm),
        "remediation_executor": create_remediation_executor_agent(llm),
        "sre_validator": create_sre_validator_agent(llm),
        "knowledge_updater": create_knowledge_updater_agent(llm),
    }

    tasks = create_ams_tasks(incident_id, service_name, initial_signals, agents)

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,  # Incident → Problem → Prevention pipeline
        verbose=True,
        memory=True,
        embedder={
            "provider": "openai",
            "config": {"model": "text-embedding-3-small"}
        }
    )

    return crew


class AMSOrchestrator:
    """Orchestrates the AMS agent pipeline with human-in-the-loop support."""

    def __init__(self, llm=None):
        self.llm = llm
        self.active_runs: Dict[str, Dict] = {}
        self.completed_runs: Dict[str, Dict] = {}

    def start_incident_response(
        self,
        incident_id: str,
        service_name: str,
        initial_signals: str,
        on_step_complete: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Start the full incident response pipeline."""
        run_id = str(uuid.uuid4())[:8]

        run_state = {
            "run_id": run_id,
            "incident_id": incident_id,
            "service_name": service_name,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "agent_steps": [],
            "result": None,
            "error": None,
            "human_approval_pending": False,
        }

        self.active_runs[run_id] = run_state

        try:
            crew = build_ams_crew(
                incident_id=incident_id,
                service_name=service_name,
                initial_signals=initial_signals,
                llm=self.llm,
            )

            result = crew.kickoff()

            run_state["status"] = "completed"
            run_state["completed_at"] = datetime.utcnow().isoformat()
            run_state["result"] = str(result)

            self.completed_runs[run_id] = run_state
            del self.active_runs[run_id]

            return run_state

        except Exception as e:
            run_state["status"] = "failed"
            run_state["error"] = str(e)
            run_state["completed_at"] = datetime.utcnow().isoformat()
            self.completed_runs[run_id] = run_state
            if run_id in self.active_runs:
                del self.active_runs[run_id]
            raise

    def approve_remediation(self, run_id: str, approved: bool, approver: str = "SRE-Lead") -> Dict:
        """Human-in-the-loop approval for high-risk remediation actions."""
        if run_id in self.active_runs:
            run = self.active_runs[run_id]
        elif run_id in self.completed_runs:
            run = self.completed_runs[run_id]
        else:
            raise ValueError(f"Run {run_id} not found")

        run["human_approval_pending"] = False
        run["approval_decision"] = {
            "approved": approved,
            "approver": approver,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return run
