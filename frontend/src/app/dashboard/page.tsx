import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { PipelineChart } from "@/components/dashboard/PipelineChart";
import { StatCard } from "@/components/dashboard/StatCard";
import { LeadList } from "@/components/leads/LeadList";

export default function DashboardPage() {
  const sampleLeads = [
    { id: "LF-101", customer_name: "Asha Catering", score: 8.7, stage: "qualified", source: "telegram" },
    { id: "LF-102", customer_name: "Northline Realty", score: 6.4, stage: "contacted", source: "instagram" },
  ];

  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8 flex items-end justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-ink/45">rep command center</p>
          <h1 className="font-display text-4xl text-ink">Pipeline dashboard</h1>
        </div>
      </div>
      <section className="grid gap-4 md:grid-cols-3">
        <StatCard label="Active Leads" value="42" tone="sea" />
        <StatCard label="Needs Approval" value="7" tone="ember" />
        <StatCard label="Won This Month" value="$18.4k" tone="pine" />
      </section>
      <section className="mt-8 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="card p-6">
          <LeadList leads={sampleLeads} />
        </div>
        <div className="space-y-6">
          <div className="card p-6">
            <PipelineChart />
          </div>
          <div className="card p-6">
            <ActivityFeed />
          </div>
        </div>
      </section>
    </main>
  );
}
