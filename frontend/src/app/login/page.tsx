"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import { LogIn, Sparkles, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${window.location.origin}/dashboard` },
    });

    if (error) setMessage({ text: error.message, type: "error" });
    else setMessage({ text: "Magic link sent! Check your inbox.", type: "success" });
    
    setLoading(false);
  };

  return (
    <main className="flex min-h-screen bg-mist">
      {/* Left: Login Form */}
      <div className="flex w-full flex-col justify-center px-6 lg:w-1/2 lg:px-20 xl:px-32">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-10 flex items-center gap-2 font-display text-2xl font-bold text-ink tracking-tight opacity-80 hover:opacity-100 transition-opacity">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-pine text-xs text-white">LF</span>
            LeadForge
          </div>

          <div className="mb-8">
            <h1 className="font-display text-4xl font-bold text-ink">Welcome back</h1>
            <p className="mt-3 text-sm text-ink/60 leading-relaxed">
              Enter your work email to access your LeadForge Mission Control. We'll send you a secure magic link.
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-ink/50">Work Email</label>
              <input
                type="email"
                required
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-2xl border border-ink/10 bg-white p-4 text-sm shadow-sm focus:border-pine focus:outline-none focus:ring-1 focus:ring-pine transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="group flex w-full items-center justify-center gap-2 rounded-2xl bg-pine p-4 text-sm font-bold text-white shadow-xl shadow-pine/20 transition-all hover:-translate-y-0.5 hover:shadow-pine/30 disabled:opacity-50 disabled:hover:translate-y-0"
            >
              {loading ? "Sending Magic Link..." : "Continue with Email"}
              <LogIn className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </button>
          </form>

          {message && (
            <div className={`mt-6 rounded-xl p-4 text-center text-sm font-medium ${message.type === "success" ? "bg-pine/10 text-pine" : "bg-ember/10 text-ember"}`}>
              {message.text}
            </div>
          )}

          <div className="mt-10 text-center text-sm text-ink/50">
            Don't have an account? <a href="/onboarding" className="font-bold text-pine hover:underline">Start Free Trial</a>
          </div>
        </div>
      </div>

      {/* Right: Graphic Panel */}
      <div className="hidden lg:relative lg:flex lg:w-1/2 lg:flex-col lg:justify-center lg:p-12">
        <div className="absolute inset-0 bg-ink">
          <img 
            src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=1600" 
            className="h-full w-full object-cover opacity-30 mix-blend-overlay"
            alt="AI Concept"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-ink via-transparent to-transparent" />
        </div>
        
        <div className="relative z-10 mx-auto max-w-lg rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur-xl shadow-2xl">
          <div className="mb-6 inline-flex rounded-2xl bg-pine/20 p-3 text-pine">
            <Sparkles className="h-6 w-6" />
          </div>
          <h2 className="font-display text-3xl font-bold text-white">The AI CRM that closes deals while you sleep.</h2>
          
          <div className="mt-8 space-y-4">
            {[
              "End-to-end autonomous lead lifecycle",
              "Sub-minute multi-channel responses",
              "Enterprise-grade web research scoring"
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3">
                <ShieldCheck className="h-5 w-5 text-pine" />
                <span className="text-sm font-medium text-mist/80">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
