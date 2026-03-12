const EVENTS = [
  "LF-101 approved via WhatsApp",
  "Voice call transferred to rep",
  "Follow-up scheduled for tomorrow 10:00",
  "New Instagram lead scored 6.4/10",
];

export function ActivityFeed() {
  return (
    <div>
      <h2 className="font-display text-2xl">Recent activity</h2>
      <div className="mt-5 space-y-3 text-sm text-ink/75">
        {EVENTS.map((event) => (
          <div key={event} className="rounded-2xl border border-ink/10 bg-white px-4 py-3">
            {event}
          </div>
        ))}
      </div>
    </div>
  );
}
