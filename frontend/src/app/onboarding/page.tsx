"use client";

import { useOnboardingStore } from "@/store/useOnboardingStore";
import { Step1Profile } from "@/components/onboarding/Step1Profile";
import { Step2Channels } from "@/components/onboarding/Step2Channels";
import { Step3DataConfig } from "@/components/onboarding/Step3DataConfig";
import { Building2, MessageCircle, Database, CheckCircle2, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";

export default function OnboardingPage() {
  const store = useOnboardingStore();
  const router = useRouter();

  const handleFinish = () => {
    // In real app, API mutation here.
    router.push("/dashboard");
  };

  const steps = [
    { title: "Business Profile", desc: "Core intelligence parameters", icon: Building2 },
    { title: "Connect Channels", desc: "Where leads engage you", icon: MessageCircle },
    { title: "Extraction Logic", desc: "Data the AI needs to collect", icon: Database },
  ];

  return (
    <main className="flex min-h-screen bg-mist selection:bg-pine/20">
      {/* Dynamic Left Sidebar Tracker */}
      <div className="hidden lg:flex w-1/3 flex-col justify-between border-r border-ink/5 bg-white/40 p-12 backdrop-blur-sm relative overflow-hidden">
        {/* Decorative Grid */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] mix-blend-overlay pointer-events-none" />
        
        <div className="relative z-10 w-full max-w-sm mx-auto h-full flex flex-col pt-12">
          <div className="mb-20 flex items-center gap-2 font-display text-2xl font-bold text-ink tracking-tight shadow-sm hover:opacity-80 transition-opacity cursor-pointer">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-pine text-sm text-white shadow-inner">LF</span>
            LeadForge
          </div>
          
          <h2 className="font-display text-4xl font-bold text-ink mb-3 tracking-tight">Initialize Core.</h2>
          <p className="text-sm font-medium text-ink/60 mb-16 leading-relaxed">Configure your AI sales agent routing parameters natively in three frictionless steps.</p>

          <div className="space-y-10 relative">
            <div className="absolute left-6 top-6 bottom-6 w-px bg-gradient-to-b from-ink/10 via-ink/20 to-transparent -z-10" />
            
            {steps.map((step, i) => {
              const num = i + 1;
              const isActive = store.step === num;
              const isPast = store.step > num;
              return (
                <div key={i} className={`relative flex items-start gap-6 transition-all duration-700 ${isActive ? 'opacity-100 translate-x-2' : isPast ? 'opacity-70' : 'opacity-30'}`}>
                  <div className={`relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border-2 transition-all duration-500 bg-white shadow-md z-10 ${
                    isActive ? 'border-pine text-pine shadow-pine/20 scale-110' : 
                    isPast ? 'border-pine bg-pine text-white scale-100' : 'border-ink/10 text-ink/40 scale-100'
                  }`}>
                    {isPast ? <CheckCircle2 className="h-6 w-6" /> : <step.icon className="h-5 w-5" />}
                  </div>
                  <div className="pt-2">
                    <h3 className={`font-display text-xl font-bold transition-colors ${isActive ? 'text-ink' : 'text-ink/70'}`}>{step.title}</h3>
                    <p className="mt-1 text-xs font-bold text-ink/40 uppercase tracking-widest leading-relaxed">{step.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Right Content Area */}
      <div className="flex w-full lg:w-2/3 flex-col relative items-center py-12 px-6 lg:justify-center overflow-y-auto">
        <div className="w-full max-w-2xl relative z-10">
          
          {/* Mobile indicator */}
          <div className="lg:hidden mb-8 flex items-center justify-between">
            <div className="flex gap-2">
              {[1, 2, 3].map((s) => (
                <div 
                  key={s} 
                  className={`h-2.5 w-12 rounded-full transition-colors duration-500 ${store.step >= s ? 'bg-pine' : 'bg-ink/10'}`} 
                />
              ))}
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-ink/40">Step {store.step} of 3</span>
          </div>

          <div className="card shadow-2xl shadow-ink/5 ring-1 ring-ink/5 border-transparent bg-white p-8 sm:p-12 transition-all duration-300 relative overflow-hidden min-h-[500px] flex flex-col justify-between">
            <div className="absolute top-0 left-0 w-full h-1.5 bg-ink/5">
              <div 
                className="h-full bg-gradient-to-r from-pine to-sea transition-all duration-700 ease-in-out" 
                style={{ width: `${(store.step / 3) * 100}%` }} 
              />
            </div>
            
            <div className="animate-[fadeIn_0.5s_ease-out] flex-1">
              {store.step === 1 && <Step1Profile />}
              {store.step === 2 && <Step2Channels />}
              {store.step === 3 && <Step3DataConfig />}
            </div>

            <div className="mt-10 flex items-center justify-between border-t border-ink/5 pt-8">
              <button 
                onClick={store.prevStep}
                disabled={store.step === 1}
                className="text-sm font-bold tracking-wider text-ink/40 uppercase hover:text-ink disabled:opacity-0 transition-opacity"
              >
                Go Back
              </button>
              
              {store.step < 3 ? (
                <button 
                  onClick={store.nextStep}
                  className="group flex items-center gap-2 rounded-2xl bg-ink px-8 py-4 text-sm font-bold text-white shadow-xl shadow-ink/10 transition-all hover:bg-pine hover:shadow-pine/30 hover:-translate-y-1"
                >
                  Continue
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </button>
              ) : (
                <button 
                  onClick={handleFinish}
                  className="group flex items-center gap-2 rounded-2xl bg-sea px-10 py-4 text-sm font-bold text-white shadow-xl shadow-sea/30 transition-all hover:bg-sea/90 hover:-translate-y-1 animate-pulse hover:animate-none"
                >
                  Deploy AI Agent Pipeline
                  <CheckCircle2 className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
