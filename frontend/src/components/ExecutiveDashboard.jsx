import React from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';

const fmt = (n) => new Intl.NumberFormat('en-US').format(n);
const fmtUSD = (n) => '$' + (n >= 1000000 ? (n / 1000000).toFixed(1) + 'M' : fmt(n));

const severityColor = { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e' };
const statusColor = { in_progress: '#3b82f6', resolved: '#22c55e', open: '#eab308', closed: '#64748b' };

const MTTR_TREND = [
  { month: 'Oct', mttr: 180 }, { month: 'Nov', mttr: 155 },
  { month: 'Dec', mttr: 142 }, { month: 'Jan', mttr: 118 },
  { month: 'Feb', mttr: 89 }, { month: 'Mar', mttr: 69 },
];

const INCIDENT_TREND = [
  { week: 'W1', incidents: 8, auto: 4 }, { week: 'W2', incidents: 6, auto: 4 },
  { week: 'W3', incidents: 9, auto: 6 }, { week: 'W4', incidents: 5, auto: 3 },
  { week: 'W5', incidents: 7, auto: 5 },
];

function MetricCard({ label, value, sub, trend, color = '#3b82f6', large }) {
  return (
    <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-5">
      <div className="text-[#64748b] text-xs font-medium uppercase tracking-wider mb-1">{label}</div>
      <div className={`font-bold ${large ? 'text-3xl' : 'text-2xl'}`} style={{ color }}>
        {value}
      </div>
      {sub && <div className="text-[#64748b] text-xs mt-1">{sub}</div>}
      {trend !== undefined && (
        <div className={`text-xs mt-1 font-medium ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
          {trend > 0 ? '▲' : '▼'} {Math.abs(trend)}% vs last month
        </div>
      )}
    </div>
  );
}

function SeverityBadge({ severity }) {
  const color = severityColor[severity] || '#64748b';
  return (
    <span
      className="px-2 py-0.5 rounded text-xs font-bold uppercase"
      style={{ background: color + '22', color, border: `1px solid ${color}44` }}
    >
      {severity}
    </span>
  );
}

export default function ExecutiveDashboard({ data }) {
  if (!data) return <div className="text-[#64748b] text-center py-20">Loading executive metrics...</div>;

  const bm = data.business_metrics || {};
  const incidents = data.active_critical_incidents || [];
  const ss = data.services_summary || {};
  const roi = data.automation_roi || {};
  const mttr = data.mttr_trend || {};

  const servicesPie = [
    { name: 'Healthy', value: ss.healthy || 4, color: '#22c55e' },
    { name: 'Degraded', value: ss.degraded || 2, color: '#f97316' },
    { name: 'Down', value: ss.down || 0, color: '#ef4444' },
  ].filter(s => s.value > 0);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#1e2d4a] to-[#1a2235] border border-[#1e3a5f] rounded-xl p-5 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Executive Operations Overview</h2>
          <p className="text-[#64748b] text-sm mt-0.5">
            Real-time business impact &amp; AMS automation metrics
          </p>
        </div>
        <div className="text-right">
          <div className="text-[#64748b] text-xs">Last updated</div>
          <div className="text-blue-400 text-sm font-mono">
            {new Date(data.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Active Critical Incident Alert */}
      {incidents.length > 0 && (
        <div className="bg-[#1a0a0a] border border-red-900 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="pulse-critical w-2.5 h-2.5 bg-red-500 rounded-full inline-block"></span>
            <span className="text-red-400 font-bold text-sm">ACTIVE CRITICAL INCIDENT</span>
          </div>
          {incidents.map(inc => (
            <div key={inc.id} className="flex items-start justify-between gap-4">
              <div>
                <div className="font-semibold text-white">{inc.title}</div>
                <div className="text-[#64748b] text-xs mt-1">{inc.id} · {inc.affected_services?.join(', ')}</div>
                <div className="text-red-300 text-xs mt-1">{inc.business_impact}</div>
              </div>
              <div className="text-right shrink-0">
                <SeverityBadge severity={inc.severity} />
                <div className="text-[#64748b] text-xs mt-1">
                  {Math.round((Date.now() - new Date(inc.created_at)) / 60000)}m ago
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* KPI Cards Row 1 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Revenue at Risk / hr"
          value={fmtUSD(bm.revenue_impact_per_hour || 744000)}
          sub="Active P1 incident"
          color="#ef4444"
          large
        />
        <MetricCard
          label="Users Affected"
          value={fmt(bm.affected_users || 2100000)}
          sub="Active degradation"
          color="#f97316"
          large
        />
        <MetricCard
          label="SLA Compliance"
          value={`${bm.sla_compliance || 96.8}%`}
          sub="Target: 99.9%"
          color={bm.sla_compliance >= 99 ? '#22c55e' : '#eab308'}
          large
        />
        <MetricCard
          label="Avg MTTR"
          value={`${bm.mttr_avg_minutes || 69.5}m`}
          sub="Down from 142m"
          trend={mttr.improvement_percent ? Math.round(mttr.improvement_percent) : 51}
          color="#3b82f6"
          large
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* MTTR Trend */}
        <div className="md:col-span-2 bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
          <div className="font-semibold text-white mb-4">MTTR Trend (6 Months)</div>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={MTTR_TREND}>
              <defs>
                <linearGradient id="mttrGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} unit="m" />
              <Tooltip
                contentStyle={{ background: '#1a2235', border: '1px solid #1e293b', borderRadius: 8 }}
                labelStyle={{ color: '#f1f5f9' }}
                formatter={(v) => [`${v}m`, 'MTTR']}
              />
              <Area type="monotone" dataKey="mttr" stroke="#3b82f6" fill="url(#mttrGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Services Status Pie */}
        <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
          <div className="font-semibold text-white mb-2">Service Health</div>
          <ResponsiveContainer width="100%" height={150}>
            <PieChart>
              <Pie data={servicesPie} cx="50%" cy="50%" innerRadius={45} outerRadius={65} paddingAngle={3} dataKey="value">
                {servicesPie.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1a2235', border: '1px solid #1e293b', borderRadius: 8 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1 mt-2">
            {servicesPie.map(s => (
              <div key={s.name} className="flex justify-between text-xs">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ background: s.color }}></span>
                  <span className="text-[#94a3b8]">{s.name}</span>
                </span>
                <span style={{ color: s.color }} className="font-medium">{s.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ROI & Automation Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          label="Cost Avoided (30 days)"
          value={fmtUSD(bm.cost_avoided_usd || 2840000)}
          sub="Via auto-remediation"
          color="#22c55e"
        />
        <MetricCard
          label="Auto-Resolved"
          value={`${roi.incidents_auto_resolved || 61}%`}
          sub="of incidents"
          color="#8b5cf6"
        />
        <MetricCard
          label="Engineer Hours Saved"
          value={fmt(roi.engineer_hours_saved || 847)}
          sub="This month"
          color="#3b82f6"
        />
      </div>

      {/* Incident Volume Chart */}
      <div className="bg-[#1a2235] border border-[#1e293b] rounded-xl p-4">
        <div className="font-semibold text-white mb-4">Incident Volume vs. Auto-Resolved (Weekly)</div>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={INCIDENT_TREND} barGap={4}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="week" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#1a2235', border: '1px solid #1e293b', borderRadius: 8 }}
            />
            <Bar dataKey="incidents" name="Total Incidents" fill="#3b82f620" stroke="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="auto" name="Auto-Resolved" fill="#22c55e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Incidents (30d)"
          value={bm.incidents_last_30_days || 23}
          sub="Total"
          color="#f1f5f9"
        />
        <MetricCard
          label="Recurrence Rate"
          value={`${bm.recurrence_rate || 12.3}%`}
          sub="Target < 10%"
          color="#eab308"
        />
        <MetricCard
          label="Txn Success Rate"
          value={`${bm.transaction_success_rate || 91.5}%`}
          sub="Target 99.5%"
          color="#f97316"
        />
        <MetricCard
          label="Open Critical"
          value={bm.critical_incidents || 1}
          sub="Incidents"
          color="#ef4444"
        />
      </div>
    </div>
  );
}
