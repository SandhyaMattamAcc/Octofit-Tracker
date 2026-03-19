"""Simulated ServiceNow tool for AMS agents."""
import random
import uuid
from datetime import datetime, timedelta
from typing import Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


SIMULATED_INCIDENTS = {
    "INC0012847": {
        "title": "Payment Service Critical Degradation",
        "severity": "1",
        "status": "In Progress",
        "affected_services": ["payment-service", "api-gateway"],
        "created_at": (datetime.utcnow() - timedelta(minutes=34)).isoformat(),
        "assigned_to": "SRE-Team-Alpha",
        "description": "Payment service experiencing 8.5% error rate and 8x latency increase",
        "cmdb_ci": "payment-service-prod",
        "business_service": "E-Commerce Platform"
    }
}

KNOWLEDGE_BASE = [
    {
        "id": "KB0004521",
        "title": "Payment DB Connection Pool Exhaustion",
        "symptoms": ["high latency", "connection timeout", "pool exhaustion"],
        "root_cause": "Database connection pool exhaustion due to long-running transactions or connection leak",
        "resolution": "1. Increase pool size temporarily\n2. Kill idle connections\n3. Identify and fix connection leak\n4. Review query performance",
        "prevention": "Implement connection pool monitoring alert at 80% utilization",
        "occurrences": 3,
        "last_occurrence": "2024-11-15"
    },
    {
        "id": "KB0003891",
        "title": "API Gateway Upstream Timeout Cascade",
        "symptoms": ["cascade failure", "gateway timeout", "upstream error"],
        "root_cause": "Upstream service degradation causing gateway connection queue overflow",
        "resolution": "1. Enable circuit breaker\n2. Increase timeout for downstream\n3. Scale upstream service",
        "prevention": "Configure circuit breaker thresholds and bulkhead patterns",
        "occurrences": 7,
        "last_occurrence": "2024-12-03"
    }
]


class ServiceNowCreateIncidentInput(BaseModel):
    title: str = Field(description="Incident title/short description")
    severity: str = Field(description="Severity level: 1=Critical, 2=High, 3=Medium, 4=Low")
    description: str = Field(description="Detailed incident description")
    affected_service: str = Field(description="Primary affected service CI name")


class ServiceNowCreateIncidentTool(BaseTool):
    name: str = "servicenow_create_incident"
    description: str = (
        "Creates a new incident ticket in ServiceNow with full ITSM workflow. "
        "Returns the incident number and initial SLA commitments."
    )
    args_schema: type[BaseModel] = ServiceNowCreateIncidentInput

    def _run(self, title: str, severity: str, description: str, affected_service: str) -> str:
        inc_num = f"INC{random.randint(1000000, 9999999)}"
        sla_map = {"1": "30 minutes", "2": "4 hours", "3": "8 hours", "4": "24 hours"}
        sla = sla_map.get(severity, "8 hours")
        return f"""
=== SERVICENOW INCIDENT CREATED ===
Incident Number: {inc_num}
Title: {title}
Severity: P{severity} - {'Critical' if severity == '1' else 'High' if severity == '2' else 'Medium'}
Status: New → Assigned
CI: {affected_service}
Created: {datetime.utcnow().isoformat()}
SLA Target: {sla}
Assignment Group: SRE-AMS-AutoRemediation
Escalation: Enabled

DESCRIPTION:
{description}

WORKFLOW TRIGGERED:
  ✓ PagerDuty alert sent to on-call SRE
  ✓ Slack notification: #incidents-critical
  ✓ War room created: {inc_num}-warroom
  ✓ Stakeholder notification queued
        """.strip()


class ServiceNowGetIncidentInput(BaseModel):
    incident_id: str = Field(description="ServiceNow incident ID (e.g., INC0012847)")


class ServiceNowGetIncidentTool(BaseTool):
    name: str = "servicenow_get_incident"
    description: str = (
        "Retrieves incident details from ServiceNow including status, "
        "timeline, work notes, and resolution details."
    )
    args_schema: type[BaseModel] = ServiceNowGetIncidentInput

    def _run(self, incident_id: str) -> str:
        if incident_id in SIMULATED_INCIDENTS:
            inc = SIMULATED_INCIDENTS[incident_id]
        else:
            inc = {
                "title": "Unknown Incident",
                "severity": "3",
                "status": "Open",
                "affected_services": ["unknown"],
                "created_at": datetime.utcnow().isoformat(),
                "assigned_to": "SRE-Team",
                "description": "Incident details not found",
                "cmdb_ci": "unknown",
                "business_service": "Unknown"
            }

        return f"""
=== SERVICENOW INCIDENT DETAILS ===
Incident: {incident_id}
Title: {inc['title']}
Severity: P{inc['severity']}
Status: {inc['status']}
Business Service: {inc['business_service']}
CI: {inc['cmdb_ci']}
Assigned To: {inc['assigned_to']}
Created: {inc['created_at']}
Affected Services: {', '.join(inc['affected_services'])}

DESCRIPTION:
{inc['description']}
        """.strip()


class ServiceNowKnowledgeSearchInput(BaseModel):
    query: str = Field(description="Search query to find relevant knowledge articles")


class ServiceNowKnowledgeTool(BaseTool):
    name: str = "servicenow_search_knowledge"
    description: str = (
        "Searches the ServiceNow knowledge base for similar past incidents, "
        "known errors, and resolution procedures."
    )
    args_schema: type[BaseModel] = ServiceNowKnowledgeSearchInput

    def _run(self, query: str) -> str:
        query_lower = query.lower()
        matches = []
        for article in KNOWLEDGE_BASE:
            score = sum(1 for s in article["symptoms"] if s in query_lower)
            if score > 0 or any(kw in query_lower for kw in article["title"].lower().split()):
                matches.append((score, article))

        if not matches:
            matches = [(1, KNOWLEDGE_BASE[0])]

        matches.sort(key=lambda x: x[0], reverse=True)
        result = f"=== SERVICENOW KNOWLEDGE SEARCH ===\nQuery: {query}\nFound {len(matches)} relevant article(s)\n\n"

        for rank, (score, article) in enumerate(matches[:2], 1):
            result += f"""
[Article #{rank}] {article['id']}: {article['title']}
  Relevance Score: {score}/3
  Previous Occurrences: {article['occurrences']}
  Last Occurrence: {article['last_occurrence']}

  ROOT CAUSE PATTERN:
    {article['root_cause']}

  PROVEN RESOLUTION STEPS:
    {article['resolution']}

  PREVENTION MEASURES:
    {article['prevention']}
"""
        return result.strip()


class ServiceNowUpdateIncidentInput(BaseModel):
    incident_id: str = Field(description="Incident ID to update")
    work_note: str = Field(description="Work note to add to the incident")
    status: str = Field(default="In Progress", description="New status for the incident")
    root_cause: str = Field(default="", description="Root cause analysis findings")


class ServiceNowUpdateIncidentTool(BaseTool):
    name: str = "servicenow_update_incident"
    description: str = (
        "Updates an existing ServiceNow incident with work notes, status changes, "
        "root cause analysis, and resolution details."
    )
    args_schema: type[BaseModel] = ServiceNowUpdateIncidentInput

    def _run(self, incident_id: str, work_note: str, status: str = "In Progress", root_cause: str = "") -> str:
        return f"""
=== SERVICENOW INCIDENT UPDATED ===
Incident: {incident_id}
Updated At: {datetime.utcnow().isoformat()}
New Status: {status}
Updated By: AMS-Agent-System

WORK NOTE ADDED:
{work_note}

{'ROOT CAUSE DOCUMENTED:' + chr(10) + root_cause if root_cause else ''}

AUDIT TRAIL:
  ✓ Change history recorded
  ✓ SLA timer updated
  ✓ Stakeholders notified of status change
  ✓ Work note indexed for knowledge mining
        """.strip()


class ServiceNowCreateProblemInput(BaseModel):
    incident_id: str = Field(description="Source incident ID")
    problem_statement: str = Field(description="Problem statement for recurring issue")
    root_cause: str = Field(description="Identified root cause")
    prevention_plan: str = Field(description="Plan to prevent recurrence")


class ServiceNowCreateProblemTool(BaseTool):
    name: str = "servicenow_create_problem"
    description: str = (
        "Creates a ServiceNow Problem record linked to an incident for root cause "
        "tracking and prevention of recurrence."
    )
    args_schema: type[BaseModel] = ServiceNowCreateProblemInput

    def _run(self, incident_id: str, problem_statement: str, root_cause: str, prevention_plan: str) -> str:
        prb_num = f"PRB{random.randint(100000, 999999)}"
        return f"""
=== SERVICENOW PROBLEM RECORD CREATED ===
Problem Number: {prb_num}
Linked Incident: {incident_id}
Created: {datetime.utcnow().isoformat()}
Status: Root Cause Analysis
Priority: High

PROBLEM STATEMENT:
{problem_statement}

ROOT CAUSE (DOCUMENTED):
{root_cause}

PREVENTION PLAN:
{prevention_plan}

WORKFLOW:
  ✓ Problem linked to incident {incident_id}
  ✓ Change Advisory Board notified
  ✓ Knowledge article creation queued
  ✓ Assigned to: Platform Engineering Team
  ✓ SLA: Resolution within 5 business days
        """.strip()
