"use client";

import Link from "next/link";
import { ArrowRight, Bot, Zap, BarChart3, Clock, TrendingUp, CheckCircle, ShieldCheck, BrainCircuit } from "lucide-react";
import { useEffect, useState } from "react";

export default function LandingPage() {
  const [leadsProcessed, setLeadsProcessed] = useState(1432);
  const [avgResponseTime, setAvgResponseTime] = useState(14);
  const [graphData, setGraphData] = useState<number[]>([]);
  const [activeChat, setActiveChat] = useState<any[]>([]);

  useEffect(() => {
    // Generate initial flat-ish graph
    setGraphData(Array.from({ length: 20 }, () => 30 + Math.random() * 20));

    // Ticking Stats
    const statsInterval = setInterval(() => {
      setLeadsProcessed((prev) => prev + Math.floor(Math.random() * 3));
      setAvgResponseTime((prev) => Math.max(9, Math.min(22, prev + (Math.random() > 0.5 ? 1 : -1))));
    }, 3000);

    // Dynamic Graph update
    const graphInterval = setInterval(() => {
      setGraphData((prev) => {
        const last = prev[prev.length - 1];
        const nextVal = Math.max(10, Math.min(90, last + (Math.random() - 0.4) * 20)); // Upward bias
        return [...prev.slice(1), nextVal];
      });
    }, 1500);

    // Simulated Agent Terminal
    const messages = [
      { text: "Lead captured from Instagram DM", type: "system" },
      { text: "Researching business legitimacy...", type: "agent" },
      { text: "Verified: 500+ employees. Score: 9.5", type: "success" },
      { text: "Rep notified via WhatsApp.", type: "system" },
      { text: "Drafting tailored engagement email...", type: "agent" },
    ];
    let msgIndex = 0;
    const chatInterval = setInterval(() => {
      setActiveChat((prev) => {
        const nextMsg = messages[msgIndex % messages.length];
        msgIndex++;
        const updated = [...prev, { id: Date.now(), ...nextMsg }];
        return updated.length > 4 ? updated.slice(1) : updated;
      });
    }, 2500);

    return () => {
      clearInterval(statsInterval);
      clearInterval(graphInterval);
      clearInterval(chatInterval);
    };
  }, []);

  // Map graph array to SVG points
  const points = graphData.map((val, i) => `${(i / (graphData.length - 1)) * 100},${100 - val}`).join(" ");

  return (
    <div className="min-h-screen bg-mist selection:bg-pine/20 overflow-hidden">
      {/* Navigation */}
      <nav className="fixed left-0 right-0 top-0 z-50 border-b border-ink/5 bg-white/80 px-6 py-4 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between">
          <div className="flex items-center gap-2 font-display text-2xl font-bold text-ink tracking-tight">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-pine text-sm text-white shadow-sm">LF</span>
            LeadForge
          </div>
          <div className="flex items-center gap-6">
            <Link href="/login" className="text-sm font-semibold text-ink/70 hover:text-ink transition-colors">Log in</Link>
            <Link href="/onboarding" className="rounded-xl bg-ink px-5 py-2.5 text-sm font-bold text-white transition-all hover:scale-105 hover:bg-pine hover:shadow-lg hover:shadow-pine/20">
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative px-6 pt-32 pb-24 lg:pt-40 lg:pb-32">
        <div className="mx-auto max-w-7xl grid lg:grid-cols-2 gap-16 items-center">

          {/* Left: Copy & CTA */}
          <div className="relative z-10 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 rounded-full border border-pine/30 bg-pine/10 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-pine mb-8 shadow-sm">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-pine opacity-75"></span>
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-pine"></span>
              </span>
              Meet your new AI Sales Agent
            </div>

            <h1 className="font-display text-5xl font-bold leading-[1.1] tracking-tight text-ink md:text-6xl lg:text-7xl">
              Never lose a lead <br />
              <span className="text-pine bg-clip-text">to slow replies.</span>
            </h1>

            <p className="mt-6 text-lg text-ink/70 md:text-xl max-w-xl mx-auto lg:mx-0 leading-relaxed font-medium">
              Capture, qualify, and close deals autonomously across WhatsApp, Instagram, Email, and Voice.
              The intelligent AI CRM that literally works 24/7.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center lg:justify-start gap-4 sm:flex-row">
              <Link href="/onboarding" className="group flex items-center gap-2 rounded-2xl bg-pine px-8 py-4 text-lg font-bold text-white shadow-xl shadow-pine/20 transition-all hover:-translate-y-1 hover:shadow-pine/30">
                Deploy Agent Now
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <span className="text-sm font-semibold text-ink/50 px-4">No credit card required.</span>
            </div>

            {/* Trust Badges */}
            <div className="mt-12 flex items-center justify-center lg:justify-start gap-6 opacity-60 grayscale">
              <div className="text-sm font-bold tracking-widest uppercase">Meta</div>
              <div className="text-sm font-bold tracking-widest uppercase">Stripe</div>
              <div className="text-sm font-bold tracking-widest uppercase">Twilio</div>
              <div className="text-sm font-bold tracking-widest uppercase">SendGrid</div>
            </div>
          </div>

          {/* Right: Dynamic Live Dashboard Preview */}
          <div className="relative w-full preserve-3d">
            {/* Background Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-pine/20 blur-[100px] rounded-full pointer-events-none -z-10" />

            <div className="relative rounded-3xl border border-white/40 bg-white/40 p-2 shadow-2xl backdrop-blur-xl rotate-1 lg:rotate-2 hover:rotate-0 transition-all duration-700 ease-out">
              <div className="rounded-2xl bg-white shadow-inner overflow-hidden border border-ink/5">

                {/* Mock Header */}
                <div className="flex items-center justify-between border-b border-ink/5 bg-mist/30 px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1.5">
                      <div className="h-3 w-3 rounded-full bg-red-400" />
                      <div className="h-3 w-3 rounded-full bg-amber-400" />
                      <div className="h-3 w-3 rounded-full bg-emerald-400" />
                    </div>
                    <span className="ml-4 text-xs font-semibold uppercase tracking-widest text-ink/40">Live Dashboard</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-pine opacity-75"></span>
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-pine"></span>
                    </span>
                    <span className="text-[10px] font-bold text-pine uppercase">Live</span>
                  </div>
                </div>

                {/* Dashboard Body */}
                <div className="p-6 grid gap-6">
                  {/* Stats Row */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-xl border border-ink/5 bg-mist/20 p-4">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-ink/40">Leads Handled Today</div>
                      <div className="mt-1 text-3xl font-bold text-ink tabular-nums flex items-baseline gap-2">
                        {leadsProcessed.toLocaleString()}
                        <TrendingUp className="h-5 w-5 text-pine" />
                      </div>
                    </div>
                    <div className="rounded-xl border border-ink/5 bg-mist/20 p-4">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-ink/40">Avg Response Time</div>
                      <div className="mt-1 text-3xl font-bold text-ink tabular-nums flex items-baseline gap-1">
                        {avgResponseTime}<span className="text-base text-ink/50">s</span>
                      </div>
                    </div>
                  </div>

                  {/* Graph */}
                  <div className="rounded-xl border border-ink/5 bg-mist/20 p-4 h-48 flex flex-col">
                    <div className="flex justify-between items-center mb-4">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-ink/40">Live Engagement Velocity</div>
                      <div className="text-xs font-bold text-pine">+23.4%</div>
                    </div>
                    <div className="flex-1 relative w-full h-full">
                      <svg className="absolute inset-0 h-full w-full overflow-visible" preserveAspectRatio="none">
                        <defs>
                          <linearGradient id="gradient" x1="0" x2="0" y1="0" y2="1">
                            <stop offset="0%" stopColor="#14532d" stopOpacity="0.2" /> {/* Pine */}
                            <stop offset="100%" stopColor="#14532d" stopOpacity="0" />
                          </linearGradient>
                        </defs>
                        <path
                          d={`M0,100 L${points} L100,100 Z`}
                          fill="url(#gradient)"
                          className="transition-all duration-1000 ease-linear"
                        />
                        <polyline
                          points={points}
                          fill="none"
                          stroke="#14532d"
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="transition-all duration-1000 ease-linear"
                        />
                      </svg>
                    </div>
                  </div>

                  {/* Live Activity Terminal */}
                  <div className="rounded-xl bg-ink p-4 font-mono text-xs shadow-inner h-40 flex flex-col justify-end overflow-hidden relative">
                    <div className="absolute top-2 left-4 text-[10px] text-mist/30 font-bold uppercase tracking-widest">Agent Logic Stream</div>
                    {/* Ghost lines for styling */}
                    <div className="absolute left-4 top-8 bottom-0 w-px bg-white/10" />

                    <div className="space-y-2 z-10 w-full">
                      {activeChat.map((msg, i) => (
                        <div
                          key={msg.id}
                          className="flex items-start gap-3 animate-[pulse_0.5s_ease-out]"
                        >
                          <div className={`mt-0.5 h-2 w-2 rounded-full shrink-0 ${msg.type === 'agent' ? 'bg-blue-400' :
                            msg.type === 'success' ? 'bg-pine' : 'bg-mist/50'
                            }`} />
                          <span className={`leading-tight ${msg.type === 'success' ? 'text-pine font-bold' :
                            msg.type === 'agent' ? 'text-blue-300' : 'text-mist/70'
                            }`}>
                            {msg.text}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Floating Images Section (AI Abstract & Agents) */}
        <div className="mx-auto mt-32 max-w-7xl">
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 overflow-hidden rounded-3xl relative h-[400px] card border border-ink/5 group">
              <img
                src="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=1600"
                alt="AI Neural Network Abstraction"
                className="absolute inset-0 h-full w-full object-cover opacity-80 transition-transform duration-1000 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-mist/95 via-mist/80 to-transparent" />
              <div className="absolute inset-y-0 left-0 p-10 flex flex-col justify-center max-w-lg">
                <BrainCircuit className="h-10 w-10 text-pine mb-4" />
                <h3 className="font-display text-4xl font-bold text-ink">Agent Orchestration</h3>
                <p className="mt-4 text-base text-ink/70 font-medium leading-relaxed">Under the hood, LangGraph perfectly orchestrates Intake, Research, Scoring, Outreach, and Voice agents in real-time. They hand off context seamlessly to close your leads like a senior account executive.</p>
              </div>
            </div>

            <div className="overflow-hidden rounded-3xl relative h-[400px] card border border-ink/5 group bg-ink text-white shadow-2xl">
              <img
                src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800"
                alt="Lead Scoring Dashboard"
                className="absolute inset-0 h-full w-full object-cover opacity-40 transition-transform duration-1000 group-hover:scale-105 mix-blend-overlay"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/80 to-transparent" />
              <div className="absolute inset-0 p-8 flex flex-col justify-end">
                <div className="flex items-center gap-2 mb-3">
                  <ShieldCheck className="h-6 w-6 text-pine" />
                  <span className="font-bold tracking-widest uppercase text-xs text-pine">Enterprise Precision</span>
                </div>
                <h3 className="text-3xl font-display font-bold text-white leading-tight">0-10 Lead Scoring in 10 Seconds.</h3>
                <p className="mt-3 text-sm text-mist/60 font-medium">Instantly identifies high-value inquiries and triggers VIP rep alerts.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="mx-auto mt-16 grid max-w-7xl gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card p-8 border border-white bg-white/60 shadow-xl shadow-ink/5 hover:-translate-y-2 transition-transform duration-300">
            <div className="mb-6 inline-flex rounded-2xl bg-gradient-to-br from-mist to-mist/50 p-4 text-pine ring-1 ring-ink/5 shadow-sm">
              <Clock className="h-8 w-8" />
            </div>
            <h3 className="font-display text-xl font-bold text-ink">Sub-Minute Responses</h3>
            <p className="mt-3 text-sm text-ink/65 leading-relaxed font-medium">Our AI agents engage leads instantly across any channel, eliminating revenue leakage from slow follow-ups.</p>
          </div>
          <div className="card p-8 border border-white bg-white/60 shadow-xl shadow-ink/5 hover:-translate-y-2 transition-transform duration-300">
            <div className="mb-6 inline-flex rounded-2xl bg-gradient-to-br from-mist to-mist/50 p-4 text-pine ring-1 ring-ink/5 shadow-sm">
              <Bot className="h-8 w-8" />
            </div>
            <h3 className="font-display text-xl font-bold text-ink">Autonomous Outreach</h3>
            <p className="mt-3 text-sm text-ink/65 leading-relaxed font-medium">Multi-sequence intelligent follow-ups that sound highly human, learn from prior interactions, and book meetings for you.</p>
          </div>
          <div className="card p-8 border border-white bg-white/60 shadow-xl shadow-ink/5 hover:-translate-y-2 transition-transform duration-300">
            <div className="mb-6 inline-flex rounded-2xl bg-gradient-to-br from-mist to-mist/50 p-4 text-pine ring-1 ring-ink/5 shadow-sm">
              <Zap className="h-8 w-8" />
            </div>
            <h3 className="font-display text-xl font-bold text-ink">Instant Web Research</h3>
            <p className="mt-3 text-sm text-ink/65 leading-relaxed font-medium">Every lead is instantly researched across the web for legitimacy and scored from 0-10 before you even see them.</p>
          </div>
          <div className="card p-8 border border-white bg-white/60 shadow-xl shadow-ink/5 hover:-translate-y-2 transition-transform duration-300">
            <div className="mb-6 inline-flex rounded-2xl bg-gradient-to-br from-mist to-mist/50 p-4 text-pine ring-1 ring-ink/5 shadow-sm">
              <BarChart3 className="h-8 w-8" />
            </div>
            <h3 className="font-display text-xl font-bold text-ink">Phone-First CRM Control</h3>
            <p className="mt-3 text-sm text-ink/65 leading-relaxed font-medium">Control your entire pipeline without opening a laptop. Approve or reject leads directly via WhatsApp smart buttons.</p>
          </div>
        </div>
      </main>

      {/* Footer CTA */}
      <footer className="bg-ink text-center py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=1600')] opacity-5 mix-blend-overlay bg-cover bg-center" />
        <div className="relative z-10 mx-auto max-w-3xl px-6">
          <h2 className="font-display text-4xl font-bold text-white mb-6">Ready to stop losing deals?</h2>
          <p className="text-mist/70 mb-10 text-lg">Onboard your business in under 3 minutes. Zero coding required.</p>
          <Link href="/onboarding" className="inline-flex items-center gap-2 rounded-2xl bg-pine px-10 py-5 text-lg font-bold text-white shadow-xl shadow-pine/20 transition-transform hover:scale-105">
            <ShieldCheck className="h-6 w-6" />
            Start Free Setup
          </Link>
        </div>
      </footer>
    </div>
  );
}
