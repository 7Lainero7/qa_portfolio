export interface Expense {
  id: number;
  title: string;
  amount_cents: number;
  category: string;
  created_at: string;
}

export interface CreateExpensePayload {
  title: string;
  amount_cents: number;
  category?: string;
}