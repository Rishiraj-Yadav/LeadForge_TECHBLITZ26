import { Send } from "lucide-react";
import { MessageBubble } from "./MessageBubble";

export function ChatWindow() {
  const dummyMessages = [
    { id: 1, text: "Hi, I need catering for a party of 50 next Saturday", isAI: false },
    { id: 2, text: "Hello! I can certainly help with that. Are you looking for a specific type of cuisine for the party of 50?", isAI: true },
    { id: 3, text: "Mexican food would be great.", isAI: false },
    { id: 4, text: "Excellent choice! We offer a full taco bar that's very popular for parties of that size. Do you have any dietary restrictions we need to accommodate?", isAI: true },
  ];

  return (
    <div className="flex h-full flex-col bg-mist/30">
      <div className="flex h-16 items-center justify-between border-b border-ink/10 px-6 bg-white">
        <div>
          <h2 className="font-semibold text-ink">Asha Catering Inquiry</h2>
          <p className="text-xs text-ink/50">via WhatsApp • Waiting for response</p>
        </div>
        <div className="flex gap-2">
          <button className="rounded-lg bg-pine px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-pine/90">
            Takeover Chat
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6">
        {dummyMessages.map((msg) => (
          <MessageBubble key={msg.id} message={msg.text} isAI={msg.isAI} />
        ))}
      </div>
      
      <div className="border-t border-ink/10 bg-white p-4">
        <div className="relative">
          <input 
            type="text" 
            placeholder="AI is handling this conversation. Click 'Takeover Chat' to reply manually." 
            disabled
            className="w-full rounded-xl border border-ink/10 bg-mist/50 py-3 pl-4 pr-12 text-sm disabled:opacity-75 focus:border-pine/50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-pine/50" 
          />
          <button disabled className="absolute right-2 top-2 rounded-lg bg-ink/10 p-1.5 text-ink/40">
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
