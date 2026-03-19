/**
 * API client for AMS Dashboard backend.
 * Falls back to mock data when backend is unavailable.
 */

const BASE_URL = '/api/v1';

const MOCK_DELAY = () => new Promise(r => setTimeout(r, 300 + Math.random() * 400));

// ─── Mock data (mirrors backend data/mock_data.py) ──────────────────────────

const now = new Date();
const minsAgo = (m) => new Date(now - m * 60000).toISOString();
const hoursAgo = (h) => new Date(now - h * 3600000).toISOString();

export const MOCK_DATA = {
  incidents: [
    {
      id: 'INC0012847',
      title: 'Payment Service Critical Degradation',
      severity: 'critical',
      status: 'in_progress',
      affected_services: ['payment-service', 'api-gateway', 'order-service'],
      business_impact: '~$12,400/min revenue impact, 2.1M users affected',
      business_impact_score: 95,
      root_cause: 'Database connection pool exhaustion (0/50 available) causing cascade timeout',
      remediation_actions: [
        '✅ AUTO: Reset connection pool (LOW risk) — Executed',
        '✅ AUTO: Scale payment-service to 8 replicas (MEDIUM risk) — Executed',
        '⏳ PENDING APPROVAL: Increase DB max_connections to 200 (HIGH risk)',
      ],
      validation_results: 'Error rate recovering: 8.5% → 2.1%. Awaiting human approval for DB change.',
      created_at: minsAgo(34),
      updated_at: minsAgo(2),
      mttr_minutes: null,
      assigned_to: 'SRE-Team-Alpha',
      agent_phase: 'remediation',
    },
    {
      id: 'INC0012831',
      title: 'Auth Service Latency Spike',
      severity: 'high',
      status: 'resolved',
      affected_services: ['auth-service', 'user-service'],
      business_impact: '$2,100/min impact, 340K users affected during peak',
      business_impact_score: 72,
      root_cause: 'Memory leak in JWT validation cache causing GC pressure',
      remediation_actions: [
        '✅ AUTO: Rolling restart of auth-service pods (LOW risk) — Executed',
        '✅ AUTO: Cleared JWT cache (LOW risk) — Executed',
      ],
      validation_results: '✅ GO: All SLOs recovered. P99 latency: 45ms (SLO: 200ms).',
      created_at: hoursAgo(3.2),
      updated_at: hoursAgo(2.1),
      mttr_minutes: 64,
      assigned_to: 'SRE-Team-Beta',
      agent_phase: 'completed',
    },
    {
      id: 'INC0012819',
      title: 'Recommendation Engine Timeout',
      severity: 'medium',
      status: 'resolved',
      affected_services: ['recommendation-service'],
      business_impact: '$890/min impact, degraded UX for 1.2M users',
      business_impact_score: 43,
      root_cause: 'ML model inference timeout due to unoptimized feature vector computation',
      remediation_actions: [
        '✅ AUTO: Increased timeout threshold (LOW risk) — Executed',
        '✅ AUTO: Enabled fallback to cached recommendations (LOW risk) — Executed',
      ],
      validation_results: '✅ GO: Service restored. Permanent fix scheduled.',
      created_at: hoursAgo(8.75),
      updated_at: hoursAgo(7.5),
      mttr_minutes: 75,
      assigned_to: 'SRE-Team-Alpha',
      agent_phase: 'completed',
    },
  ],

  agentPipeline: [
    {
      agent_name: 'Signal Detection & Correlation',
      task_description: 'Detect and correlate anomaly signals across payment-service and downstream',
      status: 'completed',
      result: 'CORRELATION REPORT: Primary anomaly in payment-db (connection pool exhaustion). Cascading to payment-service (8.5% errors) → api-gateway (3.1% errors). Blast radius: 3 services, 2.1M users. Severity: CRITICAL (confidence: 96%)',
      started_at: minsAgo(33),
      completed_at: minsAgo(30),
      requires_approval: false,
      icon: '🔍',
    },
    {
      agent_name: 'Business Impact Analyzer',
      task_description: 'Quantify revenue, SLA, and user impact of the incident',
      status: 'completed',
      result: 'IMPACT REPORT: Revenue impact $12,400/min ($744K/hr). 2.1M active users affected. SLA P1 breach in 23 min if unresolved. Business impact score: 95/100.',
      started_at: minsAgo(30),
      completed_at: minsAgo(27),
      requires_approval: false,
      icon: '📊',
    },
    {
      agent_name: 'Root Cause Analyzer',
      task_description: 'Identify definitive root cause via distributed trace analysis',
      status: 'completed',
      result: 'ROOT CAUSE: Database connection pool exhaustion (0/50 connections). Triggered by long-running transaction from payment-service v2.4.1 (deployed 2h ago). Evidence: 7,850ms pool wait time in traces. Pattern: Known (KB0004521, 3rd occurrence). Confidence: 97%',
      started_at: minsAgo(27),
      completed_at: minsAgo(22),
      requires_approval: false,
      icon: '🔬',
    },
    {
      agent_name: 'Safe Remediation Executor',
      task_description: 'Execute safe remediation with guardrails and human-in-the-loop',
      status: 'completed',
      result: 'REMEDIATION EXECUTED:\n✅ LOW RISK (auto): Connection pool reset → DONE\n✅ MEDIUM RISK (auto): Scale to 8 replicas → DONE\n⏳ HIGH RISK (awaiting approval): Increase DB max_connections 100→200\nRollback plan documented.',
      started_at: minsAgo(22),
      completed_at: minsAgo(15),
      requires_approval: true,
      icon: '⚡',
    },
    {
      agent_name: 'SRE Signal Validator',
      task_description: 'Validate remediation success via SLO/SLI recovery signals',
      status: 'completed',
      result: 'VALIDATION: Partial recovery.\n✅ Error rate: 8.5% → 2.1%\n⚠️ P99 Latency: 8,432ms → 3,200ms (target <2,000ms)\n⚠️ Connection pool: 0 → 23/50\nNO-GO: DB change pending approval.',
      started_at: minsAgo(15),
      completed_at: minsAgo(8),
      requires_approval: false,
      icon: '✅',
    },
    {
      agent_name: 'Knowledge Updater',
      task_description: 'Update knowledge base and create prevention plan for recurrence avoidance',
      status: 'running',
      result: null,
      started_at: minsAgo(8),
      completed_at: null,
      requires_approval: false,
      icon: '📚',
    },
  ],

  serviceHealth: [
    { service: 'payment-service', status: 'degraded', availability: 91.5, error_rate: 8.5, avg_latency_ms: 2300, p99_latency_ms: 8900, throughput_rps: 142, apdex_score: 0.42 },
    { service: 'auth-service', status: 'healthy', availability: 99.98, error_rate: 0.02, avg_latency_ms: 45, p99_latency_ms: 120, throughput_rps: 890, apdex_score: 0.98 },
    { service: 'api-gateway', status: 'degraded', availability: 96.9, error_rate: 3.1, avg_latency_ms: 890, p99_latency_ms: 3200, throughput_rps: 1240, apdex_score: 0.71 },
    { service: 'order-service', status: 'healthy', availability: 99.87, error_rate: 0.13, avg_latency_ms: 180, p99_latency_ms: 450, throughput_rps: 320, apdex_score: 0.95 },
    { service: 'inventory-service', status: 'healthy', availability: 99.95, error_rate: 0.05, avg_latency_ms: 65, p99_latency_ms: 180, throughput_rps: 780, apdex_score: 0.99 },
    { service: 'notification-service', status: 'healthy', availability: 99.91, error_rate: 0.09, avg_latency_ms: 95, p99_latency_ms: 280, throughput_rps: 450, apdex_score: 0.97 },
  ],

  businessMetrics: {
    revenue_impact_per_hour: 744000,
    affected_users: 2100000,
    transaction_success_rate: 91.5,
    sla_compliance: 96.8,
    open_incidents: 1,
    critical_incidents: 1,
    mttr_avg_minutes: 69.5,
    recurrence_rate: 12.3,
    incidents_last_30_days: 23,
    auto_resolved_percent: 61,
    cost_avoided_usd: 2840000,
    revenue_at_risk_usd: 744000,
  },

  sreMetrics: {
    slo_compliance: {
      'payment-service': 91.5,
      'auth-service': 99.98,
      'api-gateway': 96.9,
      'order-service': 99.87,
      'overall': 97.1,
    },
    error_budget_remaining: {
      'payment-service': -32.5,
      'auth-service': 94.2,
      'api-gateway': 68.1,
      'order-service': 88.7,
      'overall': 54.6,
    },
    change_failure_rate: 4.2,
    deployment_frequency: 12.3,
    lead_time_hours: 2.4,
    alert_fatigue_score: 34,
    false_positive_rate: 8.7,
    mean_time_to_detect_minutes: 4.2,
    mean_time_to_resolve_minutes: 69.5,
  },

  knowledgeArticles: [
    {
      id: 'KB0004521',
      incident_id: 'INC0012819',
      title: 'Payment DB Connection Pool Exhaustion',
      root_cause_pattern: 'Long-running DB transactions exhausting connection pool',
      prevention_steps: [
        'Alert: connection_pool_usage > 80% for 2 minutes',
        'Auto-remediation: Scale pool when > 90% for 1 minute',
        'Code review: Verify connection release in finally blocks',
        'Deployment gate: Load test showing pool usage < 60% at peak',
      ],
      automation_runbook: 'runbook://payment-db-pool-exhaustion-v3',
      confidence_score: 0.97,
      occurrences: 3,
    },
    {
      id: 'KB0003891',
      incident_id: 'INC0012831',
      title: 'API Gateway Upstream Cascade Timeout',
      root_cause_pattern: 'Upstream degradation causing gateway connection queue overflow',
      prevention_steps: [
        'Circuit breaker: 50% error rate threshold, 30s window',
        'Bulkhead pattern: Separate thread pools per upstream',
        'Adaptive timeout: Reduce when upstream P99 > 2x baseline',
        'Canary alerting: Detect upstream degradation within 30s',
      ],
      automation_runbook: 'runbook://api-gateway-circuit-breaker-activation',
      confidence_score: 0.91,
      occurrences: 7,
    },
  ],
};

// ─── API fetch helper ────────────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch {
    return null; // signals to use mock data
  }
}

// ─── Exported API functions ──────────────────────────────────────────────────

export async function fetchExecutiveDashboard() {
  await MOCK_DELAY();
  const data = await apiFetch('/dashboard/executive');
  if (data) return data;
  return {
    timestamp: new Date().toISOString(),
    business_metrics: MOCK_DATA.businessMetrics,
    active_critical_incidents: MOCK_DATA.incidents.filter(i => i.severity === 'critical' && i.status !== 'resolved'),
    services_summary: { total: 6, healthy: 4, degraded: 2, down: 0 },
    mttr_trend: { current_avg_minutes: 69.5, previous_avg_minutes: 142.0, improvement_percent: 51.1 },
    automation_roi: { incidents_auto_resolved: 61, cost_avoided_usd: 2840000, engineer_hours_saved: 847 },
  };
}

export async function fetchOpsDashboard() {
  await MOCK_DELAY();
  const data = await apiFetch('/dashboard/ops');
  if (data) return data;
  return {
    timestamp: new Date().toISOString(),
    incident_queue: MOCK_DATA.incidents,
    service_health: MOCK_DATA.serviceHealth,
    active_signals: [],
    agent_pipeline: {
      incident_id: 'INC0012847',
      phases: MOCK_DATA.agentPipeline,
      human_approval_pending: true,
      overall_status: 'running',
    },
    ops_summary: { open_incidents: 1, pending_approvals: 1, auto_actions_today: 14, signals_processed_today: 847 },
  };
}

export async function fetchSREDashboard() {
  await MOCK_DELAY();
  const data = await apiFetch('/dashboard/sre');
  if (data) return data;
  const sre = MOCK_DATA.sreMetrics;
  return {
    timestamp: new Date().toISOString(),
    sre_metrics: sre,
    service_reliability: MOCK_DATA.serviceHealth,
    slo_details: Object.entries(sre.slo_compliance)
      .filter(([k]) => k !== 'overall')
      .map(([service, compliance]) => ({
        service,
        slo_target: 99.9,
        current_compliance: compliance,
        error_budget_remaining: sre.error_budget_remaining[service] ?? 100,
        status: compliance >= 99.0 ? 'ok' : compliance >= 97.0 ? 'warning' : 'breach',
      })),
    validation_pipeline: MOCK_DATA.agentPipeline,
    knowledge_base: MOCK_DATA.knowledgeArticles,
    reliability_trends: {
      mttr_minutes: sre.mean_time_to_resolve_minutes,
      mttd_minutes: sre.mean_time_to_detect_minutes,
      alert_fatigue_score: sre.alert_fatigue_score,
      false_positive_rate: sre.false_positive_rate,
    },
  };
}

export async function approveRemediation(incident_id, approved, approver = 'SRE-Lead') {
  await MOCK_DELAY();
  const data = await apiFetch('/agents/approve', {
    method: 'POST',
    body: JSON.stringify({ incident_id, approved, approver }),
  });
  if (data) return data;
  return {
    incident_id,
    approved,
    approver,
    timestamp: new Date().toISOString(),
    message: approved
      ? `Remediation approved by ${approver}. Executing high-risk actions.`
      : `Remediation rejected by ${approver}. High-risk actions cancelled.`,
  };
}

export async function triggerAgentRun(service_name = 'payment-service', incident_id = null) {
  await MOCK_DELAY();
  const params = new URLSearchParams({ service_name, ...(incident_id ? { incident_id } : {}) });
  const data = await apiFetch(`/agents/run?${params}`, { method: 'POST' });
  if (data) return data;
  return {
    run_id: Math.random().toString(36).slice(2, 10),
    incident_id: incident_id || `INC${Math.floor(Math.random() * 9999999)}`,
    service_name,
    status: 'running',
    started_at: new Date().toISOString(),
    demo_mode: true,
  };
}
