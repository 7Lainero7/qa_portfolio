import React, { useState, useEffect } from 'react';
import { ExpenseForm } from './components/ExpenseForm';
import { ExpenseList } from './components/ExpenseList';
import { fetchExpenses } from './api';
import { Expense } from './types';

function App() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadExpenses = async () => {
    try {
      setLoading(true);
      const data = await fetchExpenses();
      setExpenses(data);
      setLoadError(null);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Не удалось загрузить расходы');
      console.error('Failed to load expenses', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExpenses();
  }, []);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Expense Tracker (QA Testing UI)</h1>
      {loadError && (
        <div data-testid="error-message" role="alert" style={{ color: 'red', marginBottom: '10px' }}>
          {loadError}
        </div>
      )}
      <ExpenseForm onExpenseAdded={loadExpenses} />
      {loading ? <p>Загрузка...</p> : <ExpenseList expenses={expenses} onExpenseDeleted={loadExpenses} />}
    </div>
  );
}

export default App;