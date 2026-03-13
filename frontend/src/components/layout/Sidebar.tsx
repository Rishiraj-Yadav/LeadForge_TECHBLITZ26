"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, MessageSquare, LineChart, Settings, Bell, Search } from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Leads", href: "/dashboard/leads", icon: Users },
    { name: "Conversations", href: "/dashboard/conversations", icon: MessageSquare },
    { name: "Analytics", href: "/dashboard/analytics", icon: LineChart },
  ];

  return (
    <div className="flex h-screen w-64 flex-col border-r border-ink/10 bg-white shadow-sm fixed top-0 left-0 z-10 transition-transform">
      <div className="flex h-16 items-center px-6 border-b border-ink/5">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-pine text-white flex items-center justify-center font-bold text-lg">
            LF
          </div>
          <span className="text-xl font-display font-bold text-ink tracking-tight">LeadForge</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-mist text-pine"
                  : "text-ink/70 hover:bg-mist/50 hover:text-ink"
              }`}
            >
              <Icon className={`h-5 w-5 ${isActive ? "text-pine" : "text-ink/50"}`} />
              {item.name}
            </Link>
          );
        })}
      </div>

      <div className="p-3 border-t border-ink/10">
        <Link
          href="/dashboard/settings"
          className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
            pathname === "/dashboard/settings"
              ? "bg-mist text-pine"
              : "text-ink/70 hover:bg-mist/50 hover:text-ink"
          }`}
        >
          <Settings className="h-5 w-5 text-ink/50" />
          Settings
        </Link>
      </div>
    </div>
  );
}
