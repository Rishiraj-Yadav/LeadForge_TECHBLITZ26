import { create } from "zustand";

type LeadUiState = {
  selectedLeadId: string | null;
  setSelectedLeadId: (selectedLeadId: string | null) => void;
};

export const useLeadsStore = create<LeadUiState>((set) => ({
  selectedLeadId: null,
  setSelectedLeadId: (selectedLeadId) => set({ selectedLeadId }),
}));
