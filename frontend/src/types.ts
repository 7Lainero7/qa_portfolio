interface Expense {
  id: number;
  title: string;
  amount_cents: number;
  category: string;
  created_at: string;
}

interface CreateExpensePayload {
  title: string;
  amount_cents: number;
  category?: string;
}

export type { Expense, CreateExpensePayload };