import React, { useState, useEffect, useCallback } from 'react';
import ExecutiveDashboard from './components/ExecutiveDashboard.jsx';
import OpsDashboard from './components/OpsDashboard.jsx';
import SREDashboard from './components/SREDashboard.jsx';
import {
  fetchExecutiveDashboard,
  fetchOpsDashboard,
  fetchSREDashboard,
  triggerAgentRun,
} from './utils/api.js';

const VIEWS = [
  {
    id: 'executive',
    label: 'Executive',
    icon: '👔',
    desc: 'Business impact & ROI',
  },
  {
    id: 'ops',
    label: 'Operations',
    icon: '🖥️',
    desc: 'Incident queue & agent pipeline',
  },
  {
    id: 'sre',
    label: 'SRE',
    icon: '🔧',
    desc: 'SLOs, reliability & knowledge',
  },
];

const AGENT_ICONS = ['🔍', '📊', '🔬', '⚡', '✅', '📚'];
const AGENT_NAMES = [
  'Signal Detector',
  'Impact Analyzer',
  'Root Cause Analyzer',
  'Remediation Executor',
  'SRE Validator',
  'Knowledge Updater',
];

function AgentStatusBar({ running }) {
  const [activeAgent, setActiveAgent] = useState(0);

  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setActiveAgent(a => (a + 1) % AGENT_ICONS.length), 2000);
    return () => clearInterval(t);
  }, [running]);

  return (
    <div className={`flex items-center gap-1 text-xs ${running ? '' : 'opacity-40'}`}>
      {AGENT_ICONS.map((icon, i) => (
        <span
          key={i}
          title={AGENT_NAMES[i]}
          className={`transition-all duration-300 ${
            running && i === activeAgent ? 'scale-125' : 'scale-100 opacity-50'
          }`}
        >
          {icon}
        </span>
      ))}
      {running && <span className="ml-1 text-blue-400 animate-pulse">processing...</span>}
    </div>
  );
}

export default function App() {
  const [view, setView] = useState('ops');
  const [data, setData] = useState({ executive: null, ops: null, sre: null });
  const [loading, setLoading] = useState(false);
  const [agentRunning, setAgentRunning] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [triggerCount, setTriggerCount] = useState(0);

  const loadData = useCallback(async (v) => {
    setLoading(true);
    try {
      let result;
      if (v === 'executive') result = await fetchExecutiveDashboard();
      else if (v === 'ops') result = await fetchOpsDashboard();
      else result = await fetchSREDashboard();

      setData(prev => ({ ...prev, [v]: result }));
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData(view);
  }, [view, loadData]);

  // Auto-refresh every 30s
  useEffect(() => {
    const t = setInterval(() => loadData(view), 30000);
    return () => clearInterval(t);
  }, [view, loadData]);

  async function handleTriggerAgent() {
    setAgentRunning(true);
    setTriggerCount(c => c + 1);
    try {
      await triggerAgentRun('payment-service', 'INC0012847');
      // Simulate agent running for 4 seconds then reload
      await new Promise(r => setTimeout(r, 4000));
      await loadData(view);
    } finally {
      setAgentRunning(false);
    }
  }

  const currentData = data[view];

  return (
    <div className="min-h-screen bg-[#0a0e1a]">
      {/* Top Navigation */}
      <header className="bg-[#111827] border-b border-[#1e293b] sticky top-0 z-50">
        <div className="max-w-screen-2xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            {/* Logo + Title */}
            <div className="flex items-center gap-3 shrink-0">
              <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-lg">
                🤖
              </div>
              <div>
                <div className="font-bold text-white text-sm leading-tight">
                  Agentic AMS Dashboard
                </div>
                <div className="text-[#64748b] text-xs">CrewAI · ServiceNow · Dynatrace</div>
              </div>
            </div>

            {/* View Tabs */}
            <nav className="flex gap-1">
              {VIEWS.map(v => (
                <button
                  key={v.id}
                  onClick={() => setView(v.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    view === v.id
                      ? 'bg-blue-600 text-white'
                      : 'text-[#64748b] hover:text-white hover:bg-[#1e293b]'
                  }`}
                >
                  <span className="mr-1">{v.icon}</span>
                  {v.label}
                </button>
              ))}
            </nav>

            {/* Right controls */}
            <div className="flex items-center gap-3 shrink-0">
              <AgentStatusBar running={agentRunning} />

              <button
                onClick={() => loadData(view)}
                disabled={loading}
                className="text-xs px-2 py-1 bg-[#1e293b] hover:bg-[#1a2235] text-[#64748b] hover:text-white rounded transition-colors disabled:opacity-50"
                title="Refresh"
              >
                {loading ? '⟳' : '↻'} Refresh
              </button>

              <button
                onClick={handleTriggerAgent}
                disabled={agentRunning}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                  agentRunning
                    ? 'bg-blue-900/50 text-blue-400 cursor-not-allowed border border-blue-800'
                    : 'bg-blue-600 hover:bg-blue-500 text-white'
                }`}
              >
                {agentRunning ? '🤖 Agents Running...' : '⚡ Run Agents'}
              </button>

              {lastUpdated && (
                <div className="text-[#64748b] text-xs hidden md:block">
                  {lastUpdated.toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* View Header */}
      <div className="bg-[#111827]/50 border-b border-[#1e293b]">
        <div className="max-w-screen-2xl mx-auto px-4 py-2">
          <div className="flex items-center gap-2 text-xs text-[#64748b]">
            <span>AMS</span>
            <span>›</span>
            <span className="text-white">{VIEWS.find(v => v.id === view)?.label} View</span>
            <span>—</span>
            <span>{VIEWS.find(v => v.id === view)?.desc}</span>

            {/* Architecture badges */}
            <div className="ml-auto flex items-center gap-2">
              {['CrewAI', 'Hierarchical', 'Human-in-loop', 'Guardrails'].map(tag => (
                <span key={tag} className="px-1.5 py-0.5 bg-[#1e293b] rounded text-[10px] text-[#64748b]">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-screen-2xl mx-auto px-4 py-5">
        {loading && !currentData ? (
          <div className="flex items-center justify-center py-20 gap-3">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full agent-running"></div>
            <span className="text-[#64748b]">Loading {VIEWS.find(v => v.id === view)?.label} dashboard...</span>
          </div>
        ) : (
          <>
            {view === 'executive' && <ExecutiveDashboard data={currentData} />}
            {view === 'ops' && (
              <OpsDashboard
                data={currentData}
                onApprovalAction={() => setTimeout(() => loadData('ops'), 500)}
              />
            )}
            {view === 'sre' && <SREDashboard data={currentData} />}
          </>
        )}
      </main>

      {/* Architecture Footer */}
      <footer className="border-t border-[#1e293b] bg-[#111827]/30 mt-8">
        <div className="max-w-screen-2xl mx-auto px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4 text-xs text-[#64748b]">
            <div className="flex items-center gap-4">
              <span>🤖 <strong className="text-[#94a3b8]">6 CrewAI Agents</strong></span>
              <span>→ Signal Detection</span>
              <span>→ Impact Analysis</span>
              <span>→ Root Cause</span>
              <span>→ Remediation</span>
              <span>→ SRE Validation</span>
              <span>→ Knowledge Update</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                ServiceNow (simulated)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span>
                Dynatrace (simulated)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-yellow-500 rounded-full"></span>
                Human-in-loop Guardrails
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
