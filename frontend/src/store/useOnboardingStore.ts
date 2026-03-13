import { create } from 'zustand';

interface OnboardingState {
  step: number;
  businessName: string;
  industry: string;
  contactNumber: string;
  businessHours: string;
  servicesOffered: string;

  // channels
  hasWhatsApp: boolean;
  hasInstagram: boolean;
  hasEmail: boolean;
  hasWebsiteForm: boolean;

  // Custom Fields
  fields: { id: string; name: string; required: boolean }[];
  
  // Actions
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateField: (field: keyof OnboardingState, value: any) => void;
  addField: (name: string, required: boolean) => void;
  removeField: (id: string) => void;
}

export const useOnboardingStore = create<OnboardingState>((set) => ({
  step: 1,
  businessName: '',
  industry: '',
  contactNumber: '',
  businessHours: '9:00 AM - 5:00 PM',
  servicesOffered: '',

  hasWhatsApp: true,
  hasInstagram: false,
  hasEmail: false,
  hasWebsiteForm: false,

  fields: [
    { id: '1', name: 'Name', required: true },
    { id: '2', name: 'Email or Phone', required: true },
  ],

  setStep: (step) => set({ step }),
  nextStep: () => set((state) => ({ step: state.step + 1 })),
  prevStep: () => set((state) => ({ step: Math.max(1, state.step - 1) })),
  updateField: (field, value) => set({ [field]: value }),
  
  addField: (name, required) => set((state) => ({
    fields: [...state.fields, { id: Math.random().toString(36).substring(7), name, required }]
  })),
  removeField: (id) => set((state) => ({
    fields: state.fields.filter((f) => f.id !== id)
  })),
}));
