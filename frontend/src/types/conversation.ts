export type Conversation = {
  id: string;
  lead_id: string;
  channel: string;
  intent?: string | null;
  sentiment: number;
};
