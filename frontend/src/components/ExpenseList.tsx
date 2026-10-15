import React from 'react';
import { Expense } from '../types';
import { deleteExpense } from '../api';

interface Props {
  expenses: Expense[];
  onExpenseDeleted: () => void;
}

export const ExpenseList: React.FC<Props> = ({ expenses, onExpenseDeleted }) => {
  // Сортировка по убыванию id (новые сверху)
  const sortedExpenses = [...expenses].sort((a, b) => b.id - a.id);

  const handleDelete = async (id: number) => {
    try {
      await deleteExpense(id);
      onExpenseDeleted();
    } catch (err) {
      console.error('Failed to delete expense', err);
    }
  };

  const formatRubles = (cents: number) => {
    return `${(cents / 100).toFixed(2)} ₽`;
  };

  return (
    <div data-testid="expense-list" style={{ border: '1px solid #ccc', padding: '15px' }}>
      {sortedExpenses.length === 0 ? (
        <p>Нет расходов</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #000' }}>
              <th style={{ textAlign: 'left', padding: '8px' }}>ID</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>Title</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>Amount</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>Category</th>
              <th style={{ textAlign: 'left', padding: '8px' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {sortedExpenses.map((expense) => (
              <tr key={expense.id} data-testid="expense-row" style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '8px' }}>{expense.id}</td>
                <td style={{ padding: '8px' }}>{expense.title}</td>
                <td style={{ padding: '8px' }}>{formatRubles(expense.amount_cents)}</td>
                <td style={{ padding: '8px' }}>{expense.category}</td>
                <td style={{ padding: '8px' }}>
                  <button
                    data-testid="delete-button"
                    onClick={() => handleDelete(expense.id)}
                    style={{ color: 'red', cursor: 'pointer', padding: '4px 8px' }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};