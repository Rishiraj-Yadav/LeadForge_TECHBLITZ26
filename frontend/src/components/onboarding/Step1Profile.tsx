"use client";

import { useOnboardingStore } from "@/store/useOnboardingStore";

export function Step1Profile() {
  const store = useOnboardingStore();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-ink">Business Profile</h2>
        <p className="text-ink/60 text-sm mt-1">Tell us about your business so the AI can understand your context.</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-ink mb-1">Business Name</label>
          <input 
            type="text" 
            className="w-full rounded-xl border border-ink/10 bg-mist/50 p-3 text-sm focus:border-pine focus:ring-1 focus:ring-pine outline-none" 
            placeholder="e.g. Asha Catering"
            value={store.businessName}
            onChange={(e) => store.updateField("businessName", e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-ink mb-1">Industry Type</label>
          <select 
            className="w-full rounded-xl border border-ink/10 bg-mist/50 p-3 text-sm focus:border-pine focus:ring-1 focus:ring-pine outline-none"
            value={store.industry}
            onChange={(e) => store.updateField("industry", e.target.value)}
          >
            <option value="">Select industry...</option>
            <option value="Restaurant">Restaurant / Catering</option>
            <option value="Real Estate">Real Estate</option>
            <option value="Hotel">Hotel / Hospitality</option>
            <option value="Software">Software / SaaS</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Contact Number</label>
            <input 
              type="text" 
              className="w-full rounded-xl border border-ink/10 bg-mist/50 p-3 text-sm focus:border-pine focus:ring-1 focus:ring-pine outline-none" 
              placeholder="+1 (555) 000-0000"
              value={store.contactNumber}
              onChange={(e) => store.updateField("contactNumber", e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Business Hours</label>
            <input 
              type="text" 
              className="w-full rounded-xl border border-ink/10 bg-mist/50 p-3 text-sm focus:border-pine focus:ring-1 focus:ring-pine outline-none" 
              placeholder="9 AM - 6 PM"
              value={store.businessHours}
              onChange={(e) => store.updateField("businessHours", e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-ink mb-1">Services/Products Offered</label>
          <textarea 
            rows={3}
            className="w-full rounded-xl border border-ink/10 bg-mist/50 p-3 text-sm focus:border-pine focus:ring-1 focus:ring-pine outline-none" 
            placeholder="Briefly describe what you sell. The AI will use this to answer questions."
            value={store.servicesOffered}
            onChange={(e) => store.updateField("servicesOffered", e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}
