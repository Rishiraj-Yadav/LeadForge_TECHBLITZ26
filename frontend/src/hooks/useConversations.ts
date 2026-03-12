"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "@/lib/api";
import type { Conversation } from "@/types/conversation";

export function useConversations(leadId: string) {
  return useQuery({
    queryKey: ["conversations", leadId],
    queryFn: () => fetchJson<Conversation[]>(`/api/v1/leads/${leadId}/conversations`),
    enabled: Boolean(leadId),
  });
}
