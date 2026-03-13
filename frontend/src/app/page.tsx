import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-hero-radial">
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div className="space-y-6">
            <p className="inline-flex rounded-full border border-ember/20 bg-white/60 px-4 py-2 text-sm text-ember">
              Multi-agent sales orchestration for SMB teams
            </p>
            <h1 className="font-display text-5xl leading-tight text-ink sm:text-6xl">
              Capture, qualify, and close leads before they go cold.
            </h1>
            <p className="max-w-2xl text-lg text-ink/75">
              LeadForge routes inbound leads through research, scoring, rep approval, outreach,
              follow-up, and voice handling without forcing your team back to a desktop CRM.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link className="rounded-full bg-ink px-6 py-3 text-white" href="/dashboard">
                Open Dashboard
              </Link>
              <Link className="rounded-full border border-ink/15 px-6 py-3" href="/onboarding">
                Start Onboarding
              </Link>
            </div>
          </div>
          <div className="card p-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="metric">
                <div className="text-sm uppercase tracking-[0.2em] text-ink/45">first response</div>
                <div className="mt-2 text-4xl font-semibold text-pine">&lt; 60s</div>
              </div>
              <div className="metric">
                <div className="text-sm uppercase tracking-[0.2em] text-ink/45">research time</div>
                <div className="mt-2 text-4xl font-semibold text-sea">&lt; 5s</div>
              </div>
              <div className="metric sm:col-span-2">
                <div className="text-sm uppercase tracking-[0.2em] text-ink/45">channels</div>
                <div className="mt-2 text-lg text-ink/80">
                  Website forms, Instagram, Telegram, email, voice, and manual entry.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
