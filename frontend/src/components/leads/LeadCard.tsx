import { LeadScoreBar } from "./LeadScoreBar";

export function LeadCard({ lead }: { lead: { id: string; customer_name: string; score: number; stage: string; source: string } }) {
  return (
    <article className="rounded-3xl border border-ink/10 bg-white p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm uppercase tracking-[0.2em] text-ink/45">{lead.source}</div>
          <h3 className="mt-1 text-xl font-semibold text-ink">{lead.customer_name}</h3>
          <p className="mt-2 text-sm text-ink/65">Lead ID: {lead.id}</p>
        </div>
        <span className="rounded-full bg-mist px-3 py-1 text-sm capitalize text-ink/75">{lead.stage}</span>
      </div>
      <div className="mt-5">
        <LeadScoreBar score={lead.score} />
      </div>
    </article>
  );
}
