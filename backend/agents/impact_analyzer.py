"""Agent 2: Business Impact Analyzer Agent."""
from crewai import Agent
from backend.tools import DynatraceTopologyTool, ServiceNowGetIncidentTool, ServiceNowKnowledgeTool


def create_impact_analyzer_agent(llm=None) -> Agent:
    """Creates the Business Impact Analysis Agent.

    Responsibilities:
    - Quantify business impact in revenue, users, and SLA terms
    - Map technical incidents to business services
    - Calculate business impact score for prioritization
    - Identify affected stakeholders and SLA commitments at risk
    """
    return Agent(
        role="Business Impact Analyzer",
        goal=(
            "Quantify the full business impact of technical incidents by mapping service degradation "
            "to revenue loss, user impact, and SLA compliance risk. Provide executive-ready impact "
            "assessments with concrete financial and operational metrics."
        ),
        backstory=(
            "You bridge the gap between technical incidents and business consequences. With a background "
            "in both software engineering and business analysis, you understand how milliseconds of "
            "latency translate to lost revenue and abandoned carts. You have deep knowledge of SLA "
            "commitments, customer contracts, and the reputational cost of outages. Your impact reports "
            "are used by C-suite executives to make resource allocation decisions during incidents. "
            "You always quantify uncertainty and provide confidence ranges rather than false precision."
        ),
        tools=[
            DynatraceTopologyTool(),
            ServiceNowGetIncidentTool(),
            ServiceNowKnowledgeTool(),
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=4,
        **({"llm": llm} if llm else {})
    )
