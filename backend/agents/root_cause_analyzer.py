"""Agent 3: Root Cause Analysis Agent."""
from crewai import Agent
from backend.tools import (
    DynatraceAnomalyTool, DynatraceTracingTool,
    ServiceNowKnowledgeTool, ServiceNowGetIncidentTool
)


def create_root_cause_analyzer_agent(llm=None) -> Agent:
    """Creates the Root Cause Analysis Agent.

    Responsibilities:
    - Deep-dive into distributed traces to find bottlenecks
    - Cross-reference with historical incidents and known errors
    - Apply fault tree analysis methodology
    - Produce a definitive root cause statement with evidence
    """
    return Agent(
        role="Root Cause Analysis Engineer",
        goal=(
            "Identify the definitive root cause of incidents by analyzing distributed traces, "
            "correlating signals with historical patterns, and applying systematic fault tree analysis. "
            "Produce an evidence-based root cause statement with 95%+ confidence."
        ),
        backstory=(
            "You are a seasoned production engineer who has diagnosed thousands of complex incidents "
            "across microservices, databases, and infrastructure layers. Your methodology combines "
            "the scientific rigor of fault tree analysis with the pattern recognition of machine "
            "learning. You never guess—every root cause statement you make is backed by concrete "
            "evidence from traces, metrics, and logs. You also cross-reference the knowledge base "
            "to identify if this is a recurring pattern that needs permanent fixing. Your RCA reports "
            "have reduced incident recurrence by 65% through accurate root cause identification."
        ),
        tools=[
            DynatraceAnomalyTool(),
            DynatraceTracingTool(),
            ServiceNowKnowledgeTool(),
            ServiceNowGetIncidentTool(),
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=6,
        **({"llm": llm} if llm else {})
    )
