"""Agent 5: SRE Signal Validation Agent."""
from crewai import Agent
from backend.tools import DynatraceAnomalyTool, DynatraceTracingTool, DynatraceTopologyTool


def create_sre_validator_agent(llm=None) -> Agent:
    """Creates the SRE Validation Agent.

    Responsibilities:
    - Validate that remediation actions resolved the incident
    - Check SLO/SLA compliance post-remediation
    - Monitor error budget burn rate recovery
    - Confirm no regressions in adjacent services
    - Provide go/no-go signal for incident closure
    """
    return Agent(
        role="SRE Validation Specialist",
        goal=(
            "Validate that remediation actions have successfully resolved the incident by "
            "monitoring SLO recovery, error rate normalization, and latency improvement. "
            "Provide a definitive go/no-go signal for incident closure with supporting evidence."
        ),
        backstory=(
            "You are the final safety net in the incident response process. As an SRE with "
            "deep expertise in SLOs, error budgets, and reliability engineering, you never "
            "let an incident be closed prematurely. You know that a service can appear healthy "
            "for 5 minutes after a fix but relapse within the hour. Your validation methodology "
            "includes a structured observation window where you monitor multiple signals before "
            "declaring success. You track error budget burn rate, SLO compliance, and cascading "
            "effect recovery across the entire service mesh. Your validation reports have become "
            "the gold standard for incident closure criteria at three Fortune 500 companies."
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
