export function LeadScoreBar({ score }: { score: number }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm text-ink/65">
        <span>Lead score</span>
        <span>{score}/10</span>
      </div>
      <div className="h-3 rounded-full bg-ink/10">
        <div className="h-3 rounded-full bg-ember" style={{ width: `${score * 10}%` }} />
      </div>
    </div>
  );
}
