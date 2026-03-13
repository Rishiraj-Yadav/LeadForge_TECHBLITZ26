"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "@/lib/api";
import type { Lead } from "@/types/lead";

export function useLeads() {
  return useQuery({
    queryKey: ["leads"],
    queryFn: () => fetchJson<Lead[]>("/api/v1/leads/"),
  });
}
