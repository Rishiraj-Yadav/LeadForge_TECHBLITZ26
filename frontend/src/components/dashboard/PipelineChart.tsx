const STAGES = [
  { name: "New", value: 12 },
  { name: "Contacted", value: 9 },
  { name: "Qualified", value: 7 },
  { name: "Proposal", value: 4 },
  { name: "Won", value: 2 },
];

export function PipelineChart() {
  return (
    <div>
      <h2 className="font-display text-2xl">Pipeline mix</h2>
      <div className="mt-5 space-y-4">
        {STAGES.map((stage) => (
          <div key={stage.name}>
            <div className="mb-1 flex justify-between text-sm text-ink/65">
              <span>{stage.name}</span>
              <span>{stage.value}</span>
            </div>
            <div className="h-3 rounded-full bg-ink/10">
              <div className="h-3 rounded-full bg-sea" style={{ width: `${stage.value * 8}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
