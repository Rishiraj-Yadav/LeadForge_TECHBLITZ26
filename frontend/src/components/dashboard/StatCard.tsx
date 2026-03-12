export function StatCard({ label, value, tone }: { label: string; value: string; tone: "sea" | "ember" | "pine" }) {
  const toneClass = {
    sea: "text-sea",
    ember: "text-ember",
    pine: "text-pine",
  }[tone];

  return (
    <div className="metric">
      <div className="text-sm uppercase tracking-[0.2em] text-ink/45">{label}</div>
      <div className={`mt-2 text-4xl font-semibold ${toneClass}`}>{value}</div>
    </div>
  );
}
