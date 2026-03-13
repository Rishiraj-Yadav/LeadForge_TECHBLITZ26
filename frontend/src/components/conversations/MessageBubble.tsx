export function MessageBubble({ message, isAI }: { message: string, isAI: boolean }) {
  return (
    <div className={`mb-4 flex w-full ${isAI ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm ${
          isAI 
            ? 'bg-pine text-white rounded-br-sm' 
            : 'bg-white border border-ink/10 text-ink rounded-bl-sm'
        }`}
      >
        {message}
      </div>
    </div>
  );
}
