export type Lead = {
  id: string;
  source: string;
  customer_name: string | null;
  customer_phone?: string | null;
  customer_email?: string | null;
  score: number;
  stage: string;
  rep_decision: string;
};
