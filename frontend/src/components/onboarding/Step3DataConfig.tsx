"use client";

import { useOnboardingStore } from "@/store/useOnboardingStore";
import { Plus, X } from "lucide-react";

export function Step3DataConfig() {
  const store = useOnboardingStore();

  const defaultSuggestions = store.industry === "Restaurant" 
    ? ["Number of guests", "Date/Time", "Event Type", "Dietary restrictions"]
    : store.industry === "Real Estate"
    ? ["Location", "Budget", "Property Type", "Timeline"]
    : ["Company Size", "Budget", "Goal"];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-ink">AI Data Extraction</h2>
        <p className="text-ink/60 text-sm mt-1">What specific information must the AI collect before transferring the lead to you?</p>
      </div>

      <div className="space-y-4">
        {store.fields.map((field) => (
          <div key={field.id} className="flex items-center gap-3 bg-white p-3 rounded-xl border border-ink/10 shadow-sm">
            <div className="flex-1">
              <input 
                type="text" 
                value={field.name} 
                className="w-full text-sm font-medium bg-transparent outline-none"
                readOnly
              />
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${field.required ? 'bg-ember/10 text-ember' : 'bg-mist text-ink/50'}`}>
                {field.required ? 'Required' : 'Optional'}
              </span>
              <button 
                onClick={() => store.removeField(field.id)}
                className="text-ink/30 hover:text-ember transition-colors p-1"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
        
        <div className="pt-2">
          <p className="text-xs uppercase tracking-wider text-ink/40 mb-3 font-semibold">Suggested for {store.industry || 'your business'}</p>
          <div className="flex flex-wrap gap-2">
            {defaultSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => store.addField(suggestion, true)}
                className="flex items-center gap-1 rounded-full border border-ink/10 bg-mist/50 px-3 py-1.5 text-xs text-ink/70 hover:bg-mist hover:text-ink transition-colors"
              >
                <Plus className="h-3 w-3" />
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
