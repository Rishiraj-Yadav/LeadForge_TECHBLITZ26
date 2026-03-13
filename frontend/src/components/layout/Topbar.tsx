import { Bell, Search } from "lucide-react";

export function Topbar() {
  return (
    <header className="sticky top-0 z-10 flex h-16 w-full items-center justify-between border-b border-ink/5 bg-white/80 px-6 backdrop-blur">
      <div className="flex w-full items-center gap-4 md:w-auto">
        <div className="relative w-full max-w-md md:w-80">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-ink/40" />
          <input
            type="text"
            placeholder="Search leads, conversations..."
            className="h-9 w-full rounded-md border border-ink/10 bg-mist/50 pl-9 pr-4 text-sm text-ink placeholder:text-ink/40 focus:border-pine/50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-pine/50"
          />
        </div>
      </div>
      
      <div className="flex items-center justify-end gap-4 md:gap-6">
        <button className="relative text-ink/60 hover:text-ink transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-ember text-[9px] font-bold text-white">
            3
          </span>
        </button>
        <div className="h-8 w-8 rounded-full bg-sea text-white flex items-center justify-center text-sm font-semibold select-none cursor-pointer">
          JD
        </div>
      </div>
    </header>
  );
}
