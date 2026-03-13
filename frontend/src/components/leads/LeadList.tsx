import { LeadCard } from "./LeadCard";

export function LeadList({ leads }: { leads: Array<{ id: string; customer_name: string; score: number; stage: string; source: string }> }) {
  return (
    <div>
      <h2 className="font-display text-2xl">Active leads</h2>
      <div className="mt-5 space-y-4">
        {leads.map((lead) => (
          <LeadCard key={lead.id} lead={lead} />
        ))}
      </div>
    </div>
  );
}
