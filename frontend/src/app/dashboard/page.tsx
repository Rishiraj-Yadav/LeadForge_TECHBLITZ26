"use client";

import { useEffect, useState } from "react";
import { TrendingUp, Users, Clock, Target, Activity, Zap, Server, Database, Globe, BrainCircuit } from "lucide-react";
import { LeadList } from "@/components/leads/LeadList";

export default function DashboardPage() {
  const [activeLeads, setActiveLeads] = useState(42);
  const [pipelineTotal, setPipelineTotal] = useState(18400);
  const [avgResponse, setAvgResponse] = useState(14);
  const [velocityData, setVelocityData] = useState<number[]>([]);
  const [conversionData, setConversionData] = useState<number[]>([]);
  const [agentLogs, setAgentLogs] = useState<any[]>([]);

  // Simulation Effects
  useEffect(() => {
    setVelocityData(Array.from({ length: 24 }, () => 40 + Math.random() * 40));
    setConversionData(Array.from({ length: 12 }, () => 60 + Math.random() * 30));

    const initialLogs = [
      { id: 1, time: "Just now", agent: "Intake Agent", text: "Parsed incoming Instagram DM from @techstartup", color: "bg-blue-500" },
      { id: 2, time: "1 min ago", agent: "Scoring Agent", text: "Assigned VIP score of 9.2 to Northline Realty", color: "bg-purple-500" },
      { id: 3, time: "3 min ago", agent: "Research Agent", text: "Found $5M recent funding round for Acme Corp", color: "bg-teal-500" },
      { id: 4, time: "10 min ago", agent: "Voice Agent", text: "Completed 2m14s inbound pricing qualification call", color: "bg-ember" },
    ];
    setAgentLogs(initialLogs);

    // Ticking stats
    const statsInterval = setInterval(() => {
      setActiveLeads(prev => prev + (Math.random() > 0.7 ? 1 : 0));
      setPipelineTotal(prev => prev + (Math.random() > 0.8 ? Math.floor(Math.random() * 500) : 0));
      setAvgResponse(prev => Math.max(8, Math.min(25, prev + (Math.random() > 0.5 ? 1 : -1))));
    }, 4000);

    // Graph Live Push
    const graphInterval = setInterval(() => {
      setVelocityData(prev => {
        const nextVal = Math.max(20, Math.min(100, prev[prev.length - 1] + (Math.random() - 0.4) * 20));
        return [...prev.slice(1), nextVal];
      });
      setConversionData(prev => {
        const nextVal = Math.max(40, Math.min(95, prev[prev.length - 1] + (Math.random() - 0.5) * 10));
        return [...prev.slice(1), nextVal];
      });
    }, 2000);

    // Live Logs push
    const agents = ["Intake", "Scoring", "Outreach", "Research", "Voice", "Pipeline"];
    const actions = ["Qualified new WhatsApp lead", "Sent Day 2 Nurture Sequence", "Researched prospect via Serper", "Scored inquiry at 8.5", "Booked discovery call", "Handled pricing objection"];
    const colors = ["bg-blue-500", "bg-purple-500", "bg-pine", "bg-teal-500", "bg-ember", "bg-sea"];
    
    const logsInterval = setInterval(() => {
      setAgentLogs(prev => {
        const agentIdx = Math.floor(Math.random() * agents.length);
        const actionIdx = Math.floor(Math.random() * actions.length);
        const newLog = {
          id: Date.now(),
          time: "Just now",
          agent: `${agents[agentIdx]} Agent`,
          text: actions[actionIdx],
          color: colors[agentIdx]
        };
        return [newLog, ...prev].slice(0, 10);
      });
    }, 3500);

    return () => {
      clearInterval(statsInterval);
      clearInterval(graphInterval);
      clearInterval(logsInterval);
    };
  }, []);

  const velocityPoints = velocityData.map((v, i) => `${(i / (velocityData.length - 1)) * 100},${100 - (v * 0.8)}`).join(" ");
  const conversionPoints = conversionData.map((v, i) => `${(i / (conversionData.length - 1)) * 100},${100 - (v * 0.7)}`).join(" ");

  const sampleLeads = [
    { id: "LF-101", customer_name: "Asha Catering", score: 9.2, stage: "qualified", source: "whatsapp" },
    { id: "LF-102", customer_name: "Northline Realty", score: 8.5, stage: "contacted", source: "instagram" },
  ];

  return (
    <main className="mx-auto max-w-[1400px]">
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="flex h-6 w-6 items-center justify-center rounded bg-ink text-[10px] text-white">LF</span>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-ink/45">Rep Command Center</p>
          </div>
          <h1 className="font-display text-4xl font-bold text-ink">System Overview</h1>
        </div>
        
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl shadow-sm border border-pine/20">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-pine opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-pine"></span>
            </span>
            <span className="text-[10px] font-bold text-pine uppercase tracking-wider">LangGraph Core Active</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl shadow-sm border border-ink/5">
            <Server className="h-3 w-3 text-ink/50" />
            <span className="text-[10px] font-bold text-ink/60 uppercase tracking-wider">FastAPI Connected</span>
          </div>
        </div>
      </div>

      {/* Analytics Top Row */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-6 border-transparent bg-white shadow-sm ring-1 ring-ink/5 hover:-translate-y-1 transition-transform relative overflow-hidden">
          <div className="absolute -right-4 -top-4 opacity-[0.03] text-pine"><Users className="h-32 w-32" /></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="inline-flex rounded-xl bg-pine/10 p-2 text-pine ring-1 ring-pine/20">
                <Users className="h-5 w-5" />
              </div>
              <div className="flex items-center gap-1 text-[10px] font-bold text-pine bg-pine/10 px-2 py-1 rounded">
                <TrendingUp className="h-3 w-3" /> +14%
              </div>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-ink/40">Live Inquiries (24h)</p>
            <h3 className="mt-1 text-4xl font-bold text-ink transition-all tabular-nums">{activeLeads}</h3>
          </div>
        </div>

        <div className="card p-6 border-transparent bg-white shadow-sm ring-1 ring-ink/5 hover:-translate-y-1 transition-transform relative overflow-hidden">
          <div className="absolute -right-4 -top-4 opacity-[0.03] text-sea"><Activity className="h-32 w-32" /></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="inline-flex rounded-xl bg-sea/10 p-2 text-sea ring-1 ring-sea/20">
                <Activity className="h-5 w-5" />
              </div>
              <div className="flex items-center gap-1 text-[10px] font-bold text-sea bg-sea/10 px-2 py-1 rounded">
                <TrendingUp className="h-3 w-3" /> +32%
              </div>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-ink/40">Pipeline Won (MTD)</p>
            <h3 className="mt-1 text-4xl font-bold text-ink tabular-nums transition-all flex items-baseline gap-1">
              <span className="text-2xl text-ink/50">$</span>{(pipelineTotal / 1000).toFixed(1)}k
            </h3>
          </div>
        </div>

        <div className="card p-6 border-transparent bg-white shadow-sm ring-1 ring-ink/5 hover:-translate-y-1 transition-transform relative overflow-hidden">
          <div className="absolute -right-4 -top-4 opacity-[0.03] text-mist"><Clock className="h-32 w-32" /></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="inline-flex rounded-xl bg-mist p-2 text-ink/60 ring-1 ring-ink/10">
                <Clock className="h-5 w-5" />
              </div>
              <div className="flex items-center gap-1 text-[10px] font-bold text-pine bg-pine/10 px-2 py-1 rounded">
                Fast
              </div>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-ink/40">Avg Global Response</p>
            <div className="mt-1 flex items-baseline gap-1 tabular-nums">
              <h3 className="text-4xl font-bold text-ink">{avgResponse}</h3>
              <span className="text-sm text-ink/50 font-bold uppercase tracking-wider">sec</span>
            </div>
          </div>
        </div>
        
        <div className="card p-6 border-transparent bg-white shadow-sm ring-1 ring-ink/5 hover:-translate-y-1 transition-transform relative overflow-hidden bg-gradient-to-br from-ink to-ink/90 text-white">
          <div className="absolute -right-4 -top-4 opacity-[0.05] text-white"><Target className="h-32 w-32" /></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-5">
              <div className="inline-flex rounded-xl bg-white/10 p-2 text-white ring-1 ring-white/20">
                <Target className="h-5 w-5" />
              </div>
              <div className="flex items-center gap-1 text-[10px] font-bold text-ember bg-ember/20 px-2 py-1 rounded">
                Requires Override
              </div>
            </div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-mist/60">Human Takeovers</p>
            <h3 className="mt-1 text-4xl font-bold text-white tabular-nums">3</h3>
          </div>
        </div>
      </section>

      {/* Complex Data Visualizations */}
      <section className="mt-6 grid gap-6 lg:grid-cols-2">
        {/* Graph 1: Live Engagement Velocity */}
        <div className="card p-6 border-transparent bg-white shadow-sm ring-1 ring-ink/5 flex flex-col justify-between min-h-[300px]">
          <div className="mb-2 flex items-center justify-between">
            <div>
              <h2 className="font-display text-lg font-bold text-ink">Network Throughput</h2>
              <p className="text-xs text-ink/50 font-medium">Real-time leads processed across all channels</p>
            </div>
            <Zap className="h-4 w-4 text-pine" />
          </div>
          
          <div className="flex-1 relative w-full mt-4 border-b border-l border-ink/5 pt-4">
            <svg className="absolute inset-0 h-full w-full overflow-visible" preserveAspectRatio="none">
              <defs>
                <linearGradient id="velocityGrad" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#14532d" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#14532d" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path
                d={`M0,100 L${velocityPoints} L100,100 Z`}
                fill="url(#velocityGrad)"
                className="transition-all duration-1000 ease-linear"
              />
              <polyline
                points={velocityPoints}
                fill="none"
                stroke="#14532d"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="transition-all duration-1000 ease-linear"
              />
            </svg>
          </div>
          <div className="flex justify-between mt-2 text-[10px] font-bold text-ink/40 uppercase tracking-widest pl-1">
            <span>-60s</span><span>-30s</span><span>Now</span>
          </div>
        </div>

        {/* Graph 2: Conversion Probability */}
        <div className="card p-6 border-transparent bg-white shadow-sm ring-1 ring-ink/5 flex flex-col justify-between min-h-[300px]">
          <div className="mb-2 flex items-center justify-between">
            <div>
              <h2 className="font-display text-lg font-bold text-ink">AI Qualification Score Curve</h2>
              <p className="text-xs text-ink/50 font-medium">Moving average of web-researched lead quality</p>
            </div>
            <BrainCircuit className="h-4 w-4 text-blue-500" />
          </div>
          
          <div className="flex-1 relative w-full mt-4 border-b border-l border-ink/5 pt-4">
            <svg className="absolute inset-0 h-full w-full overflow-visible" preserveAspectRatio="none">
              <defs>
                <linearGradient id="convGrad" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.15" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path
                d={`M0,100 L${conversionPoints} L100,100 Z`}
                fill="url(#convGrad)"
                className="transition-all duration-1000 ease-linear"
              />
              <polyline
                points={conversionPoints}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="transition-all duration-1000 ease-linear"
              />
            </svg>
          </div>
          <div className="flex justify-between mt-2 text-[10px] font-bold text-ink/40 uppercase tracking-widest pl-1">
            <span>Morning</span><span>Noon</span><span>Evening</span>
          </div>
        </div>
      </section>

      {/* Main Content Areas */}
      <section className="mt-6 grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <div className="flex flex-col gap-6">
          <div className="card p-6 border-transparent bg-white shadow-sm ring-1 ring-ink/5">
            <h2 className="font-display text-lg font-bold text-ink mb-1">High Priority Pipeline</h2>
            <p className="text-xs text-ink/50 font-medium mb-6">Leads with scores &gt; 8.0 currently being engaged</p>
            <LeadList leads={sampleLeads} />
          </div>
          
          <div className="grid sm:grid-cols-3 gap-4">
             <div className="rounded-2xl border border-ink/5 bg-mist/30 p-4">
               <Globe className="h-5 w-5 text-pine mb-2" />
               <div className="text-xl font-bold text-ink">144</div>
               <div className="text-[10px] font-bold uppercase tracking-wider text-ink/50">Web Visits Handled</div>
             </div>
             <div className="rounded-2xl border border-ink/5 bg-mist/30 p-4">
               <Database className="h-5 w-5 text-blue-500 mb-2" />
               <div className="text-xl font-bold text-ink">1.2k</div>
               <div className="text-[10px] font-bold uppercase tracking-wider text-ink/50">Scraping Operations</div>
             </div>
             <div className="rounded-2xl border border-ink/5 bg-[#25D366]/10 p-4">
               <Globe className="h-5 w-5 text-[#25D366] mb-2" />
               <div className="text-xl font-bold text-ink">89</div>
               <div className="text-[10px] font-bold uppercase tracking-wider text-ink/50">WhatsApp Syncs</div>
             </div>
          </div>
        </div>

        <div className="space-y-6 flex flex-col">
          <div className="rounded-3xl border-transparent bg-ink shadow-2xl ring-1 ring-ink/5 h-full max-h-[600px] flex flex-col overflow-hidden text-mist">
            <div className="p-5 border-b border-mist/10 bg-white/5 flex items-center justify-between">
              <div>
                <h2 className="font-display text-lg font-bold flex items-center gap-2 text-white">
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400"></span>
                  </span>
                  LangGraph Subroutines
                </h2>
                <p className="text-[10px] uppercase tracking-widest text-mist/40 mt-1 font-mono">Live Execution Tail</p>
              </div>
            </div>
            
            <div className="flex-1 overflow-hidden p-5 pb-0 relative">
              <div className="absolute top-0 bottom-0 left-8 w-px bg-white/5 z-0" />
              <div className="h-full overflow-y-auto pr-2 space-y-5 pb-8 relative z-10 scrollbar-hide">
                {agentLogs.map((log) => (
                  <div key={log.id} className="flex gap-4 group animate-[fadeIn_0.3s_ease-out]">
                    <div className="flex flex-col items-center pt-1.5">
                      <div className={`h-2.5 w-2.5 rounded-full ${log.color} ring-4 ring-ink`} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] uppercase font-bold tracking-widest text-mist/30">{log.time}</span>
                        <span className="text-[10px] uppercase font-bold tracking-wider text-white bg-white/10 px-2 py-0.5 rounded-sm">{log.agent}</span>
                      </div>
                      <p className="text-sm font-medium text-mist/80 leading-snug group-hover:text-white transition-colors">{log.text}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-ink to-transparent z-20 pointer-events-none" />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
