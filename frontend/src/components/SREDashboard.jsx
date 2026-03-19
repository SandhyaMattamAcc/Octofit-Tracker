import React, { useState } from 'react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, LineChart, Line, ReferenceLine
} from 'recharts';

const SLO_TREND = [
  { time: '00:00', compliance: 99.9 }, { time: '04:00', compliance: 99.8 },
  { time: '08:00', compliance: 99.7 }, { time: '10:30', compliance: 95.2 },
  { time: '11:00', compliance: 91.5 }, { time: '11:30', compliance: 93.1 },
  { time: '12:00', compliance: 94.8 }, { time: 'Now', compliance: 97.1 },
];

const DORA_DATA = [
  { metric: 'Deploy Freq', value: 85 },
  { metric: 'Lead Time', value: 72 },
  { metric: 'MTTR', value: 68 },
  { metric: 'Change Fail', value: 92 },
  { metric: 'Availability', value: 97 },
];

function SLOBar({ service, compliance, target = 99.9, budget }) {
  const pct = Math.min(compliance, 100);
  const over = compliance < target;
  const budgetNeg = budget < 0;

  return (
    <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="font-medium text-white text-sm">{service}</div>
          <div className="text-[#64748b] text-xs">SLO: {target}% target</div>
        </div>
        <div className="text-right">
          <div className={`font-bold text-lg ${
            compliance >= 99 ? 'text-green-400' :
            compliance >= 97 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {compliance.toFixed(2)}%
          </div>
          <div className={`text-xs ${budgetNeg ? 'text-red-400' : 'text-[#64748b]'}`}>
            Budget: {budget > 0 ? '+' : ''}{budget.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* SLO Bar */}
      <div className="h-2 bg-[#0a0e1a] rounded overflow-hidden">
        <div
          className={`h-full rounded transition-all ${
            compliance >= 99 ? 'bg-green-500' :
            compliance >= 97 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
          style={{ width: `${pct}%` }}
        ></div>
      </div>

      {/* Error Budget Bar */}
      {budgetNeg ? (
        <div className="mt-1.5 h-1 bg-red-900/30 rounded overflow-hidden">
          <div className="h-full bg-red-500 w-full"></div>
        </div>
      ) : (
        <div className="mt-1.5 h-1 bg-[#0a0e1a] rounded overflow-hidden">
          <div
            className="h-full bg-blue-500/50 rounded"
            style={{ width: `${Math.min(budget, 100)}%` }}
          ></div>
        </div>
      )}

      {over && (
        <div className="mt-1.5 text-xs text-red-400 flex items-center gap-1">
          <span className="pulse-critical">●</span>
          SLO BREACH — {(target - compliance).toFixed(2)}% below target
        </div>
      )}
      {budgetNeg && (
        <div className="mt-0.5 text-xs text-red-400">
          Error budget exhausted ({Math.abs(budget).toFixed(1)}% over)
        </div>
      )}
    </div>
  );
}

function MetricTile({ label, value, unit, desc, color, good }) {
  return (
    <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
      <div className="text-[#64748b] text-xs mb-1">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-bold" style={{ color: color || (good ? '#22c55e' : '#ef4444') }}>{value}</span>
        {unit && <span className="text-[#64748b] text-xs">{unit}</span>}
      </div>
      {desc && <div className="text-[#64748b] text-xs mt-1">{desc}</div>}
    </div>
  );
}

export default function SREDashboard({ data }) {
  const [activeArticle, setActiveArticle] = useState(null);

  if (!data) return <div className="text-[#64748b] text-center py-20">Loading SRE metrics...</div>;

  const sre = data.sre_metrics || {};
  const slos = data.slo_details || [];
  const pipeline = data.validation_pipeline || [];
  const kb = data.knowledge_base || [];
  const trends = data.reliability_trends || {};

  const validationPhases = pipeline.filter(p =>
    ['SRE Signal Validator', 'Knowledge Updater'].includes(p.agent_name) ||
    p.agent_name.includes('Validator') || p.agent_name.includes('Knowledge')
  );

  return (
    <div className="space-y-5">
      {/* SRE Reliability Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricTile
          label="MTTD"
          value={sre.mean_time_to_detect_minutes || 4.2}
          unit="min"
          desc="Mean Time to Detect"
          color="#3b82f6"
          good
        />
        <MetricTile
          label="MTTR"
          value={sre.mean_time_to_resolve_minutes || 69.5}
          unit="min"
          desc="Mean Time to Resolve"
          color="#8b5cf6"
          good
        />
        <MetricTile
          label="Change Fail Rate"
          value={`${sre.change_failure_rate || 4.2}%`}
          desc="Target < 5%"
          color={sre.change_failure_rate <= 5 ? '#22c55e' : '#ef4444'}
          good
        />
        <MetricTile
          label="Alert Fatigue"
          value={sre.alert_fatigue_score || 34}
          unit="/100"
          desc={`FP Rate: ${sre.false_positive_rate || 8.7}%`}
          color={sre.alert_fatigue_score <= 40 ? '#22c55e' : '#eab308'}
          good
        />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* SLO Compliance */}
        <div className="space-y-3">
          <h3 className="font-semibold text-white">SLO Compliance & Error Budgets</h3>
          {slos.map(slo => (
            <SLOBar
              key={slo.service}
              service={slo.service}
              compliance={slo.current_compliance}
              target={slo.slo_target}
              budget={slo.error_budget_remaining}
            />
          ))}
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {/* SLO Trend */}
          <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
            <div className="font-semibold text-white mb-3 text-sm">SLO Compliance — Today</div>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={SLO_TREND}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} domain={[88, 100]} />
                <Tooltip
                  contentStyle={{ background: '#1a2235', border: '1px solid #1e293b', borderRadius: 8 }}
                  formatter={(v) => [`${v.toFixed(1)}%`, 'SLO']}
                />
                <ReferenceLine y={99.9} stroke="#22c55e" strokeDasharray="4 4" label={{ value: 'SLO', fill: '#22c55e', fontSize: 10 }} />
                <Line
                  type="monotone" dataKey="compliance" stroke="#3b82f6" strokeWidth={2}
                  dot={(props) => {
                    const { cx, cy, payload } = props;
                    return payload.compliance < 99 ? (
                      <circle key={`dot-${cx}`} cx={cx} cy={cy} r={4} fill="#ef4444" />
                    ) : <circle key={`dot-${cx}`} cx={cx} cy={cy} r={2} fill="#3b82f6" />;
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* DORA Radar */}
          <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
            <div className="font-semibold text-white mb-2 text-sm">DORA Metrics (Elite = 100)</div>
            <ResponsiveContainer width="100%" height={180}>
              <RadarChart data={DORA_DATA}>
                <PolarGrid stroke="#1e293b" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#64748b', fontSize: 10 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={false} />
                <Radar dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Agent Validation Pipeline */}
      <div>
        <h3 className="font-semibold text-white mb-3">Agent Validation Pipeline</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {pipeline.filter(p =>
            ['SRE Signal Validator', 'Knowledge Updater'].some(n => p.agent_name.includes(n.split(' ')[0]))
          ).map((phase) => (
            <div
              key={phase.agent_name}
              className={`border rounded-xl p-4 ${
                phase.status === 'completed' ? 'bg-green-900/10 border-green-900/50' :
                phase.status === 'running' ? 'bg-blue-900/10 border-blue-900/50 card-running' :
                'bg-[#1a2235] border-[#1e293b]'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm text-white">{phase.icon} {phase.agent_name}</span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  phase.status === 'completed' ? 'bg-green-900/50 text-green-400' :
                  phase.status === 'running' ? 'bg-blue-900/50 text-blue-400' :
                  'bg-[#1e293b] text-[#64748b]'
                }`}>
                  {phase.status}
                </span>
              </div>
              <div className="text-xs text-[#64748b] mb-2">{phase.task_description}</div>
              {phase.result && (
                <div className="text-xs bg-[#0a0e1a] rounded p-2 font-mono text-[#94a3b8] whitespace-pre-line">
                  {phase.result}
                </div>
              )}
              {phase.status === 'running' && (
                <div className="mt-2 h-1 bg-[#1e293b] rounded overflow-hidden">
                  <div className="h-full bg-blue-500 w-3/5" style={{ animation: 'pulse 1.5s ease-in-out infinite' }}></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Knowledge Base */}
      <div>
        <h3 className="font-semibold text-white mb-3">Knowledge Base — Learned from Incidents</h3>
        <div className="space-y-3">
          {kb.map(article => (
            <div
              key={article.id}
              onClick={() => setActiveArticle(activeArticle?.id === article.id ? null : article)}
              className="bg-[#1a2235] border border-[#1e293b] hover:border-purple-800 rounded-xl p-4 cursor-pointer transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400 font-mono text-xs">{article.id}</span>
                    <span className="text-xs bg-purple-900/30 text-purple-300 px-1.5 py-0.5 rounded">
                      {article.occurrences}x occurrences
                    </span>
                  </div>
                  <div className="font-medium text-sm text-white mt-0.5">{article.title}</div>
                  <div className="text-xs text-[#64748b] mt-0.5">{article.root_cause_pattern}</div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-green-400 font-bold">{(article.confidence_score * 100).toFixed(0)}%</div>
                  <div className="text-xs text-[#64748b]">confidence</div>
                </div>
              </div>

              {activeArticle?.id === article.id && (
                <div className="mt-3 pt-3 border-t border-[#1e293b] space-y-3">
                  <div>
                    <div className="text-xs text-[#64748b] mb-1.5 font-medium">Prevention Steps</div>
                    <ul className="space-y-1">
                      {article.prevention_steps.map((step, i) => (
                        <li key={i} className="text-xs text-[#94a3b8] flex gap-2">
                          <span className="text-green-400 shrink-0">→</span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                  {article.automation_runbook && (
                    <div className="text-xs font-mono bg-[#0a0e1a] text-blue-300 px-2 py-1 rounded inline-block">
                      {article.automation_runbook}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
