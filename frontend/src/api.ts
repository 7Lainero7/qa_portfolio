import { Expense, CreateExpensePayload } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'test-key';

const HEADERS = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const humanizeError = (status: number, statusText: string): string => {
  if (status === 401) return 'Ошибка авторизации: неверный API-ключ (401)';
  if (status === 404) return 'Ресурс не найден (404)';
  if (status === 422) return 'Невалидные данные запроса (422)';
  if (status >= 500) return `Ошибка сервера (${status})`;
  return `Ошибка: ${status} ${statusText}`.trim();
};

const handleResponse = async (res: Response) => {
  if (!res.ok) {
    throw new ApiError(res.status, humanizeError(res.status, res.statusText));
  }
  return res;
};

export const fetchExpenses = async (): Promise<Expense[]> => {
  const res = await fetch(`${API_URL}/api/expenses?limit=100&offset=0`, { headers: HEADERS });
  await handleResponse(res);
  return res.json();
};

export const createExpense = async (payload: CreateExpensePayload): Promise<Expense> => {
  const res = await fetch(`${API_URL}/api/expenses`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify(payload),
  });
  await handleResponse(res);
  return res.json();
};

export const deleteExpense = async (id: number): Promise<void> => {
  const res = await fetch(`${API_URL}/api/expenses/${id}`, {
    method: 'DELETE',
    headers: HEADERS,
  });
  await handleResponse(res);
};