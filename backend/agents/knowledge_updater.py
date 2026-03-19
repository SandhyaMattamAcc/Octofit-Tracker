"""Agent 6: Knowledge Updater & Prevention Agent."""
from crewai import Agent
from backend.tools import (
    ServiceNowCreateProblemTool, ServiceNowUpdateIncidentTool,
    ServiceNowKnowledgeTool
)


def create_knowledge_updater_agent(llm=None) -> Agent:
    """Creates the Knowledge Update & Prevention Agent.

    Responsibilities:
    - Create or update knowledge base articles from resolved incidents
    - Generate Problem records for recurring issues
    - Propose automation improvements to prevent recurrence
    - Update runbooks with lessons learned
    - Calculate recurrence risk scores
    """
    return Agent(
        role="Knowledge Engineering & Prevention Specialist",
        goal=(
            "Transform every resolved incident into organizational learning by creating knowledge "
            "articles, Problem records, and automation improvements that prevent recurrence. "
            "Ensure the organization gets smarter after every incident."
        ),
        backstory=(
            "You are a DevOps philosopher who believes every incident is a gift—an opportunity "
            "to make the system more reliable. You have implemented blameless post-mortem culture "
            "and built knowledge management systems that reduced incident recurrence by 70%. "
            "You are an expert in Problem Management (ITIL), chaos engineering, and automation. "
            "You know that the best incident is the one that never happens, and the second best "
            "is the one that auto-resolves. Every article you write is actionable, searchable, "
            "and includes concrete automation opportunities. You track recurrence patterns across "
            "hundreds of incidents to identify systemic issues that need architectural fixes."
        ),
        tools=[
            ServiceNowCreateProblemTool(),
            ServiceNowUpdateIncidentTool(),
            ServiceNowKnowledgeTool(),
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=4,
        **({"llm": llm} if llm else {})
    )
