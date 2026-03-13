"use client";

import { useState } from "react";
import { fetchJson } from "@/lib/api";

/* ── Industry presets ── */
const INDUSTRIES = [
  { id: "restaurant", label: "🍽️ Restaurant", icon: "🍽️" },
  { id: "hotel", label: "🏨 Hotel", icon: "🏨" },
  { id: "real_estate", label: "🏠 Real Estate", icon: "🏠" },
  { id: "other", label: "🏢 Other", icon: "🏢" },
] as const;

const DEFAULT_CAPTURE_FIELDS: Record<string, Record<string, { label: string; default: boolean }>> = {
  restaurant: {
    guest_count: { label: "Number of guests", default: true },
    date: { label: "Date", default: true },
    time: { label: "Time", default: true },
    event_type: { label: "Event type", default: true },
    dietary_restrictions: { label: "Dietary restrictions", default: false },
    budget: { label: "Budget", default: false },
  },
  hotel: {
    guest_count: { label: "Number of guests", default: true },
    check_in: { label: "Check-in date", default: true },
    check_out: { label: "Check-out date", default: true },
    room_type: { label: "Room type", default: false },
    budget: { label: "Budget", default: false },
  },
  real_estate: {
    property_type: { label: "Property type", default: true },
    location: { label: "Location", default: true },
    budget: { label: "Budget", default: true },
    bedrooms: { label: "Bedrooms", default: false },
  },
  other: {
    budget: { label: "Budget", default: false },
    date: { label: "Date/Timeline", default: false },
  },
};

type Step = 1 | 2 | 3 | 4;

interface RegisterResponse {
  business_id: string;
  deep_link_code: string;
  telegram_link: string;
  qr_code_base64: string;
  default_capture_fields: Record<string, boolean>;
}

export default function OnboardingPage() {
  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 1 fields
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [hours, setHours] = useState("");
  const [services, setServices] = useState("");

  // Step 2 result
  const [registerResult, setRegisterResult] = useState<RegisterResponse | null>(null);

  // Step 3 fields
  const [captureFields, setCaptureFields] = useState<Record<string, boolean>>({});
  const [welcomeMessage, setWelcomeMessage] = useState("");

  /* ── Step 1: Register Business ── */
  async function handleRegister() {
    if (!name.trim() || !industry) {
      setError("Business name and industry are required.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const result = await fetchJson<RegisterResponse>("/api/v1/onboarding/register", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          industry,
          phone: phone.trim() || undefined,
          email: email.trim() || undefined,
          business_hours: hours.trim() || undefined,
          services_offered: services.trim() || undefined,
        }),
      });
      setRegisterResult(result);

      // Initialize capture fields from industry defaults
      const defaults = DEFAULT_CAPTURE_FIELDS[industry] || DEFAULT_CAPTURE_FIELDS.other;
      const fields: Record<string, boolean> = {};
      for (const [key, cfg] of Object.entries(defaults)) {
        fields[key] = result.default_capture_fields?.[key] ?? cfg.default;
      }
      setCaptureFields(fields);

      setStep(2);
    } catch (err: any) {
      setError(err?.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  /* ── Step 3: Save Configuration ── */
  async function handleConfigure() {
    if (!registerResult) return;
    setError("");
    setLoading(true);
    try {
      await fetchJson("/api/v1/onboarding/configure", {
        method: "POST",
        body: JSON.stringify({
          business_id: registerResult.business_id,
          capture_fields: captureFields,
          welcome_message: welcomeMessage.trim() || undefined,
        }),
      });
      setStep(4);
    } catch (err: any) {
      setError(err?.message || "Configuration failed.");
    } finally {
      setLoading(false);
    }
  }

  function toggleField(key: string) {
    setCaptureFields((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  return (
    <main className="min-h-screen bg-hero-radial">
      <div className="mx-auto max-w-2xl px-6 py-12">
        {/* ── Progress bar ── */}
        <div className="mb-10">
          <div className="flex items-center justify-between text-sm text-ink/50">
            {[
              { n: 1, label: "Business Details" },
              { n: 2, label: "Connect Telegram" },
              { n: 3, label: "Configure AI" },
              { n: 4, label: "You're Live!" },
            ].map((s, i) => (
              <div key={s.n} className="flex items-center gap-2">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold transition-all ${
                    step >= s.n
                      ? "bg-ink text-white shadow-md"
                      : "bg-white text-ink/30 ring-1 ring-black/10"
                  }`}
                >
                  {step > s.n ? "✓" : s.n}
                </div>
                <span className={`hidden sm:inline ${step >= s.n ? "text-ink" : ""}`}>{s.label}</span>
                {i < 3 && (
                  <div
                    className={`mx-2 hidden h-px w-8 sm:block ${
                      step > s.n ? "bg-ink" : "bg-ink/10"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-2xl border border-clay/20 bg-clay/5 px-5 py-3 text-sm text-clay">
            {error}
          </div>
        )}

        {/* ════════════════════════════════════════════════════════
            STEP 1: Business Details
        ════════════════════════════════════════════════════════ */}
        {step === 1 && (
          <div className="card p-8 animate-in">
            <p className="text-sm uppercase tracking-[0.2em] text-ember">Step 1 of 4</p>
            <h1 className="mt-2 font-display text-3xl text-ink">Tell us about your business</h1>
            <p className="mt-2 text-ink/60">
              This helps our AI give personalized responses to your customers.
            </p>

            <div className="mt-8 space-y-5">
              {/* Business Name */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink/70">
                  Business Name <span className="text-clay">*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Royal Restaurant"
                  className="w-full rounded-xl border border-ink/10 bg-white px-4 py-3 text-ink shadow-sm outline-none transition-all focus:border-ember/40 focus:ring-2 focus:ring-ember/10"
                />
              </div>

              {/* Industry */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink/70">
                  Industry Type <span className="text-clay">*</span>
                </label>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {INDUSTRIES.map((ind) => (
                    <button
                      key={ind.id}
                      onClick={() => setIndustry(ind.id)}
                      className={`rounded-xl border px-4 py-3.5 text-center text-sm transition-all ${
                        industry === ind.id
                          ? "border-ember bg-ember/5 text-ember shadow-sm"
                          : "border-ink/10 bg-white text-ink/70 hover:border-ink/20 hover:bg-ink/[0.02]"
                      }`}
                    >
                      <div className="text-2xl">{ind.icon}</div>
                      <div className="mt-1">{ind.id.charAt(0).toUpperCase() + ind.id.slice(1).replace("_", " ")}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Contact */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-ink/70">
                    Contact Number
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full rounded-xl border border-ink/10 bg-white px-4 py-3 text-ink shadow-sm outline-none transition-all focus:border-ember/40 focus:ring-2 focus:ring-ember/10"
                  />
                </div>
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-ink/70">
                    Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="hello@business.com"
                    className="w-full rounded-xl border border-ink/10 bg-white px-4 py-3 text-ink shadow-sm outline-none transition-all focus:border-ember/40 focus:ring-2 focus:ring-ember/10"
                  />
                </div>
              </div>

              {/* Business Hours */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink/70">
                  Business Hours
                </label>
                <input
                  type="text"
                  value={hours}
                  onChange={(e) => setHours(e.target.value)}
                  placeholder="e.g., Mon-Sat 9 AM - 10 PM"
                  className="w-full rounded-xl border border-ink/10 bg-white px-4 py-3 text-ink shadow-sm outline-none transition-all focus:border-ember/40 focus:ring-2 focus:ring-ember/10"
                />
              </div>

              {/* Services */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink/70">
                  Services / Products Offered
                </label>
                <textarea
                  value={services}
                  onChange={(e) => setServices(e.target.value)}
                  placeholder="e.g., Birthday parties, Corporate events, Fine dining, Room bookings..."
                  rows={3}
                  className="w-full resize-none rounded-xl border border-ink/10 bg-white px-4 py-3 text-ink shadow-sm outline-none transition-all focus:border-ember/40 focus:ring-2 focus:ring-ember/10"
                />
              </div>
            </div>

            <button
              onClick={handleRegister}
              disabled={loading}
              className="mt-8 w-full rounded-full bg-ink px-6 py-3.5 text-white shadow-md transition-all hover:shadow-lg disabled:opacity-50"
            >
              {loading ? "Creating..." : "Continue →"}
            </button>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════
            STEP 2: Connect Telegram
        ════════════════════════════════════════════════════════ */}
        {step === 2 && registerResult && (
          <div className="card p-8 animate-in">
            <p className="text-sm uppercase tracking-[0.2em] text-ember">Step 2 of 4</p>
            <h1 className="mt-2 font-display text-3xl text-ink">Connect Telegram</h1>
            <p className="mt-2 text-ink/60">
              Link your Telegram to receive lead notifications and set up your customer bot.
            </p>

            <div className="mt-8 space-y-6">
              {/* Owner notification link */}
              <div className="rounded-2xl border border-pine/15 bg-pine/[0.03] p-5">
                <h3 className="font-semibold text-pine">📱 For You (Business Owner)</h3>
                <p className="mt-1 text-sm text-ink/60">
                  Click this link from your phone to receive lead notifications on Telegram:
                </p>
                <a
                  href={registerResult.telegram_link.replace("?start=", "?start=connect_")}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-flex items-center gap-2 rounded-full bg-pine px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:shadow-md"
                >
                  Connect My Telegram →
                </a>
                <p className="mt-2 text-xs text-ink/40">
                  Or send <code className="rounded bg-ink/5 px-1.5 py-0.5">/connect {registerResult.deep_link_code}</code> to the bot.
                </p>
              </div>

              {/* Customer QR + Link */}
              <div className="rounded-2xl border border-sea/15 bg-sea/[0.03] p-5">
                <h3 className="font-semibold text-sea">🔗 For Your Customers</h3>
                <p className="mt-1 text-sm text-ink/60">
                  Share this QR code or link with customers to start chatting with your AI assistant.
                </p>

                <div className="mt-4 flex flex-col items-center gap-4 sm:flex-row sm:items-start">
                  {/* QR Code */}
                  <div className="flex flex-col items-center">
                    <div className="rounded-2xl border border-black/5 bg-white p-3 shadow-sm">
                      <img
                        src={`data:image/png;base64,${registerResult.qr_code_base64}`}
                        alt="Customer QR Code"
                        className="h-40 w-40"
                      />
                    </div>
                    <p className="mt-2 text-xs text-ink/40">Scan to chat</p>
                  </div>

                  {/* Link */}
                  <div className="flex-1 space-y-3">
                    <div>
                      <label className="text-xs font-medium text-ink/50">Customer link</label>
                      <div className="mt-1 flex items-center gap-2">
                        <input
                          type="text"
                          readOnly
                          value={registerResult.telegram_link}
                          className="flex-1 rounded-xl border border-ink/10 bg-white px-3 py-2 text-sm text-ink/80"
                        />
                        <button
                          onClick={() => navigator.clipboard.writeText(registerResult.telegram_link)}
                          className="shrink-0 rounded-xl border border-ink/10 bg-white px-3 py-2 text-sm text-ink/60 transition-all hover:bg-ink/[0.03]"
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                    <div className="rounded-xl bg-white/80 p-3 text-xs text-ink/50">
                      <strong>Pro tip:</strong> Print the QR code and display it at your counter, add
                      the link to your Instagram bio, or share it on your website.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={() => setStep(3)}
              className="mt-8 w-full rounded-full bg-ink px-6 py-3.5 text-white shadow-md transition-all hover:shadow-lg"
            >
              Continue →
            </button>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════
            STEP 3: Configure AI Capture
        ════════════════════════════════════════════════════════ */}
        {step === 3 && (
          <div className="card p-8 animate-in">
            <p className="text-sm uppercase tracking-[0.2em] text-ember">Step 3 of 4</p>
            <h1 className="mt-2 font-display text-3xl text-ink">Configure your AI assistant</h1>
            <p className="mt-2 text-ink/60">
              Choose what information the AI should collect from customers during conversation.
            </p>

            <div className="mt-8 space-y-6">
              {/* Capture fields */}
              <div>
                <h3 className="font-semibold text-ink">What info do you need from customers?</h3>
                <div className="mt-3 space-y-2">
                  {Object.entries(DEFAULT_CAPTURE_FIELDS[industry] || DEFAULT_CAPTURE_FIELDS.other).map(
                    ([key, cfg]) => (
                      <label
                        key={key}
                        className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 transition-all ${
                          captureFields[key]
                            ? "border-ember/20 bg-ember/[0.03]"
                            : "border-ink/8 bg-white hover:bg-ink/[0.01]"
                        }`}
                      >
                        <div
                          className={`flex h-5 w-5 items-center justify-center rounded-md border transition-all ${
                            captureFields[key]
                              ? "border-ember bg-ember text-white"
                              : "border-ink/20 bg-white"
                          }`}
                        >
                          {captureFields[key] && (
                            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                        <span className="flex-1 text-sm text-ink/80">{cfg.label}</span>
                        <span className="text-xs text-ink/30">
                          {cfg.default ? "recommended" : "optional"}
                        </span>
                        <input
                          type="checkbox"
                          checked={captureFields[key] || false}
                          onChange={() => toggleField(key)}
                          className="sr-only"
                        />
                      </label>
                    )
                  )}
                </div>
              </div>

              {/* Welcome message */}
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink/70">
                  Custom Welcome Message <span className="text-ink/30">(optional)</span>
                </label>
                <textarea
                  value={welcomeMessage}
                  onChange={(e) => setWelcomeMessage(e.target.value)}
                  placeholder={`Hi! Welcome to ${name || "our business"} 👋 How can I help you today?`}
                  rows={3}
                  className="w-full resize-none rounded-xl border border-ink/10 bg-white px-4 py-3 text-ink shadow-sm outline-none transition-all focus:border-ember/40 focus:ring-2 focus:ring-ember/10"
                />
                <p className="mt-1 text-xs text-ink/40">
                  Leave blank for a smart default based on your business name.
                </p>
              </div>
            </div>

            <button
              onClick={handleConfigure}
              disabled={loading}
              className="mt-8 w-full rounded-full bg-ink px-6 py-3.5 text-white shadow-md transition-all hover:shadow-lg disabled:opacity-50"
            >
              {loading ? "Saving..." : "Finish Setup →"}
            </button>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════
            STEP 4: Success
        ════════════════════════════════════════════════════════ */}
        {step === 4 && registerResult && (
          <div className="card p-8 text-center animate-in">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-pine/10 text-3xl">
              ✅
            </div>
            <h1 className="mt-4 font-display text-3xl text-ink">You&apos;re live!</h1>
            <p className="mt-2 text-ink/60">
              Your AI assistant is now active 24/7. Customers can start chatting immediately.
            </p>

            <div className="mx-auto mt-8 max-w-sm space-y-4">
              {/* Customer link */}
              <div className="rounded-2xl border border-ink/8 bg-white/80 p-5 text-left">
                <p className="text-xs font-medium uppercase tracking-[0.15em] text-ink/40">
                  Customer link
                </p>
                <p className="mt-1 break-all text-sm font-medium text-sea">
                  {registerResult.telegram_link}
                </p>
              </div>

              {/* QR */}
              <div className="flex justify-center">
                <div className="rounded-2xl border border-black/5 bg-white p-3 shadow-sm">
                  <img
                    src={`data:image/png;base64,${registerResult.qr_code_base64}`}
                    alt="Customer QR Code"
                    className="h-32 w-32"
                  />
                </div>
              </div>

              {/* Next steps */}
              <div className="rounded-2xl border border-ember/10 bg-ember/[0.03] p-5 text-left">
                <p className="text-sm font-semibold text-ember">What happens next?</p>
                <ul className="mt-2 space-y-1.5 text-sm text-ink/60">
                  <li>→ Share the QR code / link with customers</li>
                  <li>→ AI will chat with them and capture details</li>
                  <li>→ You get Telegram notifications for new leads</li>
                  <li>→ Approve or reject with one tap</li>
                </ul>
              </div>
            </div>

            <div className="mt-8 flex justify-center gap-4">
              <a
                href="/dashboard"
                className="rounded-full bg-ink px-6 py-3 text-white shadow-md transition-all hover:shadow-lg"
              >
                Open Dashboard
              </a>
              <button
                onClick={() => navigator.clipboard.writeText(registerResult.telegram_link)}
                className="rounded-full border border-ink/15 px-6 py-3 text-ink/70 transition-all hover:bg-ink/[0.03]"
              >
                Copy Link
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
