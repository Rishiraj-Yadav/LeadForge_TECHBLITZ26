import { LeadList } from "@/components/leads/LeadList";

export default function LeadsPage() {
  const dummyLeads = [
    { id: "LF-101", customer_name: "Asha Catering", score: 8.7, stage: "qualified", source: "whatsapp" },
    { id: "LF-102", customer_name: "Northline Realty", score: 6.4, stage: "contacted", source: "instagram" },
    { id: "LF-103", customer_name: "Blue Ocean Hotel", score: 9.1, stage: "proposal", source: "email" },
    { id: "LF-104", customer_name: "John Doe", score: 4.2, stage: "lost", source: "form" },
  ];

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-8 flex items-end justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-ink">Leads Management</h1>
          <p className="mt-2 text-sm text-ink/65">Manage and track your AI-generated leads pipeline.</p>
        </div>
        <button className="rounded-lg bg-pine px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-pine/90">
          Add Lead Manually
        </button>
      </div>
      
      <div className="card p-6">
        <LeadList leads={dummyLeads} />
      </div>
    </div>
  );
}
