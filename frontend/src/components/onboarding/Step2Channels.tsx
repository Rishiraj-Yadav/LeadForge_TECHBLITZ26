"use client";

import { useOnboardingStore } from "@/store/useOnboardingStore";

export function Step2Channels() {
  const store = useOnboardingStore();

  const toggle = (field: "hasWhatsApp" | "hasInstagram" | "hasEmail" | "hasWebsiteForm") => {
    store.updateField(field, !store[field]);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-display font-semibold text-ink">Connect Channels</h2>
        <p className="text-ink/60 text-sm mt-1">Select the platforms where leads currently contact you.</p>
      </div>

      <div className="space-y-3">
        <label className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-colors ${store.hasWhatsApp ? 'border-pine bg-pine/5' : 'border-ink/10 bg-mist/50 hover:bg-mist'}`}>
          <div className="flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${store.hasWhatsApp ? 'bg-pine text-white' : 'bg-ink/10 text-ink/40'}`}>
              WA
            </div>
            <div>
              <p className="font-semibold text-ink text-sm">WhatsApp Business</p>
              <p className="text-xs text-ink/50">Used for lead capture & rep notifications</p>
            </div>
          </div>
          <input type="checkbox" className="hidden" checked={store.hasWhatsApp} onChange={() => toggle("hasWhatsApp")} />
          <div className={`h-6 w-11 rounded-full p-1 transition-colors ${store.hasWhatsApp ? 'bg-pine' : 'bg-ink/20'}`}>
            <div className={`h-4 w-4 rounded-full bg-white transition-transform ${store.hasWhatsApp ? 'translate-x-5' : 'translate-x-0'}`} />
          </div>
        </label>

        <label className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-colors ${store.hasInstagram ? 'border-pine bg-pine/5' : 'border-ink/10 bg-mist/50 hover:bg-mist'}`}>
          <div className="flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${store.hasInstagram ? 'bg-gradient-to-tr from-yellow-400 via-red-500 to-purple-500 text-white' : 'bg-ink/10 text-ink/40'}`}>
              IG
            </div>
            <div>
              <p className="font-semibold text-ink text-sm">Instagram DMs</p>
              <p className="text-xs text-ink/50">Capture leads from Meta Graph API</p>
            </div>
          </div>
          <input type="checkbox" className="hidden" checked={store.hasInstagram} onChange={() => toggle("hasInstagram")} />
          <div className={`h-6 w-11 rounded-full p-1 transition-colors ${store.hasInstagram ? 'bg-pine' : 'bg-ink/20'}`}>
            <div className={`h-4 w-4 rounded-full bg-white transition-transform ${store.hasInstagram ? 'translate-x-5' : 'translate-x-0'}`} />
          </div>
        </label>

        <label className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-colors ${store.hasWebsiteForm ? 'border-pine bg-pine/5' : 'border-ink/10 bg-mist/50 hover:bg-mist'}`}>
          <div className="flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${store.hasWebsiteForm ? 'bg-sea text-white' : 'bg-ink/10 text-ink/40'}`}>
              Web
            </div>
            <div>
              <p className="font-semibold text-ink text-sm">Website Widget</p>
              <p className="text-xs text-ink/50">Embed our LeadForge chat widget</p>
            </div>
          </div>
          <input type="checkbox" className="hidden" checked={store.hasWebsiteForm} onChange={() => toggle("hasWebsiteForm")} />
          <div className={`h-6 w-11 rounded-full p-1 transition-colors ${store.hasWebsiteForm ? 'bg-pine' : 'bg-ink/20'}`}>
            <div className={`h-4 w-4 rounded-full bg-white transition-transform ${store.hasWebsiteForm ? 'translate-x-5' : 'translate-x-0'}`} />
          </div>
        </label>
      </div>

      {store.hasWhatsApp && (
        <div className="mt-8 rounded-xl border border-pine/20 bg-pine/5 p-5">
          <h3 className="font-semibold text-pine mb-2">Connect WhatsApp Notification Bot</h3>
          <p className="text-sm text-ink/70 mb-4">
            Sales reps will approve/reject leads through WhatsApp. Scan the QR code with your phone to initialize the bot.
          </p>
          <div className="flex justify-center">
            <div className="h-40 w-40 bg-white border border-ink/10 rounded-lg flex items-center justify-center">
              {/* Dummy QR placeholder */}
              <div className="w-32 h-32 bg-[url('https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=LeadForgeTest')] bg-cover opacity-80" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
