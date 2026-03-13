import { ChatWindow } from "@/components/conversations/ChatWindow";

export default function ConversationsPage() {
  return (
    <div className="flex h-[calc(100vh-6rem)] gap-6">
      <div className="w-80 flex-shrink-0 card flex flex-col overflow-hidden">
        <div className="border-b border-ink/10 p-4">
          <h2 className="font-semibold text-ink text-lg font-display">Active Chats</h2>
          <p className="text-xs text-ink/50">3 requiring attention</p>
        </div>
        <div className="flex-1 overflow-y-auto">
          {/* Dummy chat list items */}
          <div className="cursor-pointer border-l-2 border-pine bg-mist/50 p-4 transition-colors">
            <div className="flex items-center justify-between">
              <span className="font-medium text-ink text-sm">Asha Catering</span>
              <span className="text-xs text-ink/40">2m ago</span>
            </div>
            <p className="mt-1 truncate text-xs text-ink/60">Mexican food would be great...</p>
            <div className="mt-2 flex gap-2">
              <span className="rounded bg-sky-100 px-1.5 py-0.5 text-[10px] uppercase text-sky-800 font-bold">whatsapp</span>
              <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] uppercase text-emerald-800 font-bold">score: 8.7</span>
            </div>
          </div>
          <div className="cursor-pointer border-l-2 border-transparent p-4 transition-colors hover:bg-mist/30">
            <div className="flex items-center justify-between">
              <span className="font-medium text-ink text-sm">Northline Realty</span>
              <span className="text-xs text-ink/40">1h ago</span>
            </div>
            <p className="mt-1 truncate text-xs text-ink/60">I'm looking for a 3BHK in downtown...</p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 card overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  );
}

