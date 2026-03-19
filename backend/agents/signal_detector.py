"""Agent 1: Signal Detection & Correlation Agent."""
from crewai import Agent
from backend.tools import DynatraceAnomalyTool, DynatraceTracingTool, DynatraceTopologyTool


def create_signal_detector_agent(llm=None) -> Agent:
    """Creates the Signal Detection & Correlation Agent.

    Responsibilities:
    - Monitor all observability signals across services
    - Correlate related signals to identify incident scope
    - Determine blast radius using topology data
    - Assign severity based on correlated signal patterns
    """
    return Agent(
        role="Signal Detection & Correlation Specialist",
        goal=(
            "Detect anomalous signals across all monitored services, correlate them to identify "
            "the full scope of an incident, and provide a comprehensive signal correlation report "
            "that pinpoints the primary failing component and all cascading effects."
        ),
        backstory=(
            "You are an elite Site Reliability Engineer with 10+ years of experience in "
            "observability and monitoring. You have mastered Dynatrace, Prometheus, and distributed "
            "tracing systems. You excel at pattern recognition—you can look at a flood of alerts "
            "and immediately identify which signals are symptoms vs root causes. Your correlation "
            "skills reduce alert noise by 80% and mean teams only focus on what truly matters. "
            "You follow AIOps best practices and always validate signals before raising alarms."
        ),
        tools=[
            DynatraceAnomalyTool(),
            DynatraceTracingTool(),
            DynatraceTopologyTool(),
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=5,
        **({"llm": llm} if llm else {})
    )
