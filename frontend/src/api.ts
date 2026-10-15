import { Expense, CreateExpensePayload } from './types';

const API_BASE = 'http://127.0.0.1:8000';
const HEADERS = {
  'Content-Type': 'application/json',
  'X-API-Key': 'test-key',
};

const handleResponse = async (res: Response) => {
  if (!res.ok) {
    if (res.status === 401 || res.status === 422 || res.status === 500) {
      alert(`Ошибка: ${res.status} ${res.statusText}`);
    }
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res;
};

export const fetchExpenses = async (): Promise<Expense[]> => {
  const res = await fetch(`${API_BASE}/api/expenses?limit=100&offset=0`, { headers: HEADERS });
  await handleResponse(res);
  return res.json();
};

export const createExpense = async (payload: CreateExpensePayload): Promise<Expense> => {
  const res = await fetch(`${API_BASE}/api/expenses`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify(payload),
  });
  await handleResponse(res);
  return res.json();
};

export const deleteExpense = async (id: number): Promise<void> => {
  const res = await fetch(`${API_BASE}/api/expenses/${id}`, {
    method: 'DELETE',
    headers: HEADERS,
  });
  await handleResponse(res);
};