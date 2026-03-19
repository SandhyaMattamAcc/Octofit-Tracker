import React, { useState } from 'react';
import { approveRemediation } from '../utils/api.js';

const severityColor = { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e' };
const statusBg = {
  completed: 'bg-green-900/30 border-green-800',
  running: 'bg-blue-900/30 border-blue-800',
  pending: 'bg-[#1e293b] border-[#1e293b]',
  failed: 'bg-red-900/20 border-red-900',
};

function SeverityBadge({ severity }) {
  const c = severityColor[severity] || '#64748b';
  return (
    <span className="px-2 py-0.5 rounded text-xs font-bold uppercase"
      style={{ background: c + '22', color: c, border: `1px solid ${c}44` }}>
      {severity}
    </span>
  );
}

function StatusDot({ status }) {
  const map = { healthy: '#22c55e', degraded: '#f97316', down: '#ef4444' };
  const c = map[status] || '#64748b';
  return <span className="w-2 h-2 rounded-full inline-block" style={{ background: c }}></span>;
}

function AgentCard({ phase, index }) {
  const [expanded, setExpanded] = useState(false);
  const isRunning = phase.status === 'running';
  const isDone = phase.status === 'completed';
  const isPending = phase.status === 'pending';

  return (
    <div
      className={`border rounded-lg p-3 cursor-pointer transition-all ${statusBg[phase.status] || statusBg.pending}`}
      onClick={() => phase.result && setExpanded(e => !e)}
    >
      <div className="flex items-start gap-3">
        {/* Step number / icon */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${
          isDone ? 'bg-green-900 text-green-300' :
          isRunning ? 'bg-blue-900 text-blue-300' :
          'bg-[#1e293b] text-[#64748b]'
        }`}>
          {isDone ? '✓' : isRunning ? <span className="agent-running inline-block">↻</span> : index + 1}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span className="font-medium text-sm text-white">{phase.icon} {phase.agent_name}</span>
            <div className="flex items-center gap-2 shrink-0">
              {phase.requires_approval && phase.status === 'completed' && (
                <span className="text-xs px-1.5 py-0.5 bg-yellow-900/50 text-yellow-400 border border-yellow-800 rounded">
                  Needs Approval
                </span>
              )}
              <span className={`text-xs px-1.5 py-0.5 rounded ${
                isDone ? 'bg-green-900/50 text-green-400' :
                isRunning ? 'bg-blue-900/50 text-blue-400' :
                'bg-[#1e293b] text-[#64748b]'
              }`}>
                {phase.status}
              </span>
            </div>
          </div>
          <div className="text-xs text-[#64748b] mt-0.5">{phase.task_description}</div>

          {isRunning && (
            <div className="mt-2 h-1 bg-[#1e293b] rounded overflow-hidden">
              <div className="h-full bg-blue-500 rounded" style={{ width: '65%', transition: 'width 1s ease' }}></div>
            </div>
          )}

          {expanded && phase.result && (
            <div className="mt-2 bg-[#0a0e1a] rounded p-2 text-xs font-mono text-[#94a3b8] whitespace-pre-line">
              {phase.result}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function OpsDashboard({ data, onApprovalAction }) {
  const [approving, setApproving] = useState(false);
  const [approvalResult, setApprovalResult] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);

  if (!data) return <div className="text-[#64748b] text-center py-20">Loading operations data...</div>;

  const queue = data.incident_queue || [];
  const services = data.service_health || [];
  const pipeline = data.agent_pipeline || {};
  const phases = pipeline.phases || [];
  const ops = data.ops_summary || {};
  const hasPendingApproval = pipeline.human_approval_pending;

  async function handleApproval(approved) {
    if (!pipeline.incident_id) return;
    setApproving(true);
    try {
      const result = await approveRemediation(pipeline.incident_id, approved);
      setApprovalResult({ ...result, approved });
      if (onApprovalAction) onApprovalAction(result);
    } finally {
      setApproving(false);
    }
  }

  const active = queue.find(i => i.status === 'in_progress');

  return (
    <div className="space-y-5">
      {/* Ops Summary Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Open Incidents', value: ops.open_incidents ?? 1, color: '#ef4444' },
          { label: 'Pending Approvals', value: ops.pending_approvals ?? 1, color: '#eab308' },
          { label: 'Auto-Actions Today', value: ops.auto_actions_today ?? 14, color: '#22c55e' },
          { label: 'Signals Processed', value: ops.signals_processed_today ?? 847, color: '#3b82f6' },
        ].map(m => (
          <div key={m.label} className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
            <div className="text-[#64748b] text-xs">{m.label}</div>
            <div className="text-2xl font-bold mt-1" style={{ color: m.color }}>{m.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Left: Incident Queue */}
        <div className="space-y-3">
          <h3 className="font-semibold text-white">Incident Queue</h3>
          {queue.map(inc => (
            <div
              key={inc.id}
              onClick={() => setSelectedIncident(selectedIncident?.id === inc.id ? null : inc)}
              className={`bg-[#1a2235] border rounded-xl p-4 cursor-pointer transition-all hover:border-blue-800 ${
                inc.severity === 'critical' && inc.status !== 'resolved' ? 'card-critical' : ''
              } ${selectedIncident?.id === inc.id ? 'border-blue-700' : 'border-[#1e293b]'}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-sm text-white">{inc.title}</span>
                    <SeverityBadge severity={inc.severity} />
                  </div>
                  <div className="text-xs text-[#64748b] mt-1">
                    {inc.id} · {inc.affected_services?.join(', ')}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className={`text-xs px-2 py-0.5 rounded ${
                    inc.status === 'resolved' ? 'bg-green-900/50 text-green-400' :
                    inc.status === 'in_progress' ? 'bg-blue-900/50 text-blue-400' :
                    'bg-[#1e293b] text-[#64748b]'
                  }`}>
                    {inc.status.replace('_', ' ')}
                  </div>
                  {inc.mttr_minutes && (
                    <div className="text-green-400 text-xs mt-1">MTTR: {inc.mttr_minutes}m</div>
                  )}
                </div>
              </div>

              {selectedIncident?.id === inc.id && (
                <div className="mt-3 pt-3 border-t border-[#1e293b] space-y-2">
                  {inc.business_impact && (
                    <div>
                      <div className="text-xs text-[#64748b] mb-0.5">Business Impact</div>
                      <div className="text-xs text-orange-300">{inc.business_impact}</div>
                    </div>
                  )}
                  {inc.root_cause && (
                    <div>
                      <div className="text-xs text-[#64748b] mb-0.5">Root Cause</div>
                      <div className="text-xs text-[#94a3b8]">{inc.root_cause}</div>
                    </div>
                  )}
                  {inc.remediation_actions?.length > 0 && (
                    <div>
                      <div className="text-xs text-[#64748b] mb-0.5">Remediation Actions</div>
                      {inc.remediation_actions.map((a, i) => (
                        <div key={i} className="text-xs text-[#94a3b8] font-mono">{a}</div>
                      ))}
                    </div>
                  )}
                  {inc.validation_results && (
                    <div>
                      <div className="text-xs text-[#64748b] mb-0.5">Validation</div>
                      <div className="text-xs text-[#94a3b8]">{inc.validation_results}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Right: Service Health */}
        <div className="space-y-3">
          <h3 className="font-semibold text-white">Service Health</h3>
          <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl overflow-hidden">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-[#1e293b]">
                  {['Service', 'Status', 'Err%', 'P99 (ms)', 'Apdex'].map(h => (
                    <th key={h} className="text-left text-[#64748b] px-3 py-2 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {services.map(svc => (
                  <tr key={svc.service} className="border-b border-[#1e293b]/50 hover:bg-[#111827]">
                    <td className="px-3 py-2 text-white font-medium">{svc.service}</td>
                    <td className="px-3 py-2">
                      <span className="flex items-center gap-1.5">
                        <StatusDot status={svc.status} />
                        <span className={svc.status === 'healthy' ? 'text-green-400' : 'text-orange-400'}>
                          {svc.status}
                        </span>
                      </span>
                    </td>
                    <td className={`px-3 py-2 font-mono ${svc.error_rate > 1 ? 'text-red-400' : 'text-green-400'}`}>
                      {svc.error_rate}%
                    </td>
                    <td className={`px-3 py-2 font-mono ${svc.p99_latency_ms > 2000 ? 'text-red-400' : svc.p99_latency_ms > 500 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {svc.p99_latency_ms.toLocaleString()}
                    </td>
                    <td className={`px-3 py-2 font-mono ${svc.apdex_score >= 0.9 ? 'text-green-400' : svc.apdex_score >= 0.7 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {svc.apdex_score}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Agent Pipeline */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-white">
            Agent Pipeline
            {pipeline.incident_id && (
              <span className="ml-2 text-xs text-blue-400 font-mono">→ {pipeline.incident_id}</span>
            )}
          </h3>
          <div className="text-xs text-[#64748b]">
            {phases.filter(p => p.status === 'completed').length}/{phases.length} phases complete
          </div>
        </div>

        {/* Human-in-the-loop approval banner */}
        {hasPendingApproval && !approvalResult && (
          <div className="mb-3 bg-yellow-900/20 border border-yellow-700 rounded-xl p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-yellow-400 font-semibold">⚠ Human Approval Required</div>
                <div className="text-xs text-[#94a3b8] mt-1">
                  Safe Remediation Agent is requesting approval for a HIGH RISK action:
                  <br />
                  <span className="font-mono text-yellow-300">Increase DB max_connections: 100 → 200</span>
                  <br />
                  Rollback: Revert postgresql.conf and reload. Risk: DB restart required if misconfigured.
                </div>
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={() => handleApproval(false)}
                  disabled={approving}
                  className="px-3 py-1.5 bg-red-900/50 hover:bg-red-900 text-red-300 border border-red-800 rounded text-xs font-medium transition-colors disabled:opacity-50"
                >
                  Reject
                </button>
                <button
                  onClick={() => handleApproval(true)}
                  disabled={approving}
                  className="px-3 py-1.5 bg-green-900/50 hover:bg-green-900 text-green-300 border border-green-800 rounded text-xs font-medium transition-colors disabled:opacity-50"
                >
                  {approving ? 'Processing...' : 'Approve'}
                </button>
              </div>
            </div>
          </div>
        )}

        {approvalResult && (
          <div className={`mb-3 rounded-xl p-3 text-xs border ${
            approvalResult.approved
              ? 'bg-green-900/20 border-green-800 text-green-300'
              : 'bg-red-900/20 border-red-800 text-red-300'
          }`}>
            {approvalResult.approved ? '✅' : '❌'} {approvalResult.message}
          </div>
        )}

        <div className="space-y-2">
          {phases.map((phase, i) => (
            <AgentCard key={phase.agent_name} phase={phase} index={i} />
          ))}
        </div>
      </div>
    </div>
  );
}
