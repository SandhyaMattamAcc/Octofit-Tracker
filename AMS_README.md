# Agentic AMS Dashboard

> AI-powered Application Management Services with CrewAI agents for autonomous incident detection, root cause analysis, safe remediation, and prevention.

## Architecture

```
Layer            │ Implementation
─────────────────┼──────────────────────────────────────────
Agents           │ CrewAI (6 Specialized Agents)
Orchestration    │ Sequential Crew (Incident → Problem → Prevention)
Tools            │ ServiceNow + Dynatrace (simulated)
Process          │ Signal → Impact → RCA → Remediation → Validate → Learn
Governance       │ Guardrails + Human-in-loop (HIGH risk approval)
Outcome          │ Reduced MTTR + Prevented Recurrence
```

## Agent Pipeline

```
🔍 Signal Detection & Correlation
   ↓  Dynatrace anomaly fetch, trace analysis, topology blast radius
📊 Business Impact Analyzer
   ↓  Revenue/user/SLA quantification, executive briefing
🔬 Root Cause Analyzer
   ↓  Fault tree analysis, trace deep-dive, KB cross-reference
⚡ Safe Remediation Executor
   ↓  Risk classification → AUTO (low/med) | HUMAN APPROVAL (high)
✅ SRE Signal Validator
   ↓  SLO recovery, error budget, GO/NO-GO decision
📚 Knowledge Updater
   └  Problem record, KB article, automation proposals
```

## Dashboard Views

| View | Audience | Key Content |
|------|----------|-------------|
| **Executive** | C-Suite | Revenue impact, MTTR trend, automation ROI, SLA compliance |
| **Operations** | Ops Team | Incident queue, agent pipeline, human-in-loop approvals, service health |
| **SRE** | SRE Team | SLO/SLI compliance, error budgets, DORA metrics, knowledge base |

## Project Structure

```
/
├── backend/
│   ├── agents/          # 6 CrewAI agents (one per pipeline stage)
│   ├── tools/           # Simulated ServiceNow & Dynatrace tools
│   ├── crew/            # Hierarchical crew orchestration
│   ├── api/             # FastAPI routes (/api/v1/...)
│   ├── models/          # Pydantic schemas
│   ├── data/            # Mock data generator
│   └── main.py          # FastAPI entrypoint
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ExecutiveDashboard.jsx
│       │   ├── OpsDashboard.jsx
│       │   └── SREDashboard.jsx
│       ├── utils/api.js  # API client with mock fallback
│       └── App.jsx       # Main app with view switcher
├── requirements.txt
├── docker-compose.yml
└── start.sh
```

## Quick Start

### Backend (FastAPI)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
# Dashboard: http://localhost:3000
```

### Docker Compose

```bash
cp .env.example .env
# Add your OPENAI_API_KEY for live agent execution
docker-compose up
```

## Live Agent Execution

Set `OPENAI_API_KEY` to enable real CrewAI agent execution. Without it, the dashboard uses rich mock data demonstrating the full agent workflow.

```bash
export OPENAI_API_KEY=sk-...
uvicorn backend.main:app --reload
# Click "⚡ Run Agents" in the dashboard
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/dashboard/executive` | Executive metrics |
| GET | `/api/v1/dashboard/ops` | Operations dashboard |
| GET | `/api/v1/dashboard/sre` | SRE metrics & SLOs |
| GET | `/api/v1/incidents` | Incident queue |
| POST | `/api/v1/agents/run` | Trigger agent crew |
| POST | `/api/v1/agents/approve` | Human-in-loop approval |
| GET | `/api/v1/services/health` | Service health |
| GET | `/api/v1/knowledge` | Knowledge base |

## Key Features

- **Human-in-the-loop**: High-risk remediations require explicit SRE approval before execution
- **Guardrails**: Automatic risk classification (LOW/MEDIUM auto-execute, HIGH requires approval)
- **Knowledge Loop**: Every resolved incident generates a knowledge article and prevention plan
- **Simulated Tools**: Full ServiceNow + Dynatrace simulation — no external services required
- **DORA Metrics**: Deployment frequency, lead time, MTTR, change failure rate
- **Error Budgets**: Real-time SLO compliance and error budget burn rate tracking
