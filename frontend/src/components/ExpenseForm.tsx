import React, { useState } from 'react';
import { createExpense } from '../api';
import { CreateExpensePayload } from '../types';

interface Props {
    onExpenseAdded: () => void;
}

export const ExpenseForm: React.FC<Props> = ({ onExpenseAdded }) => {
    const [title, setTitle] = useState('');
    const [amount, setAmount] = useState('');
    const [category, setCategory] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Клиентская валидация
        if (!title.trim()) {
            alert('Title не может быть пустым');
            return;
        }
        const amountNum = Number(amount);
        if (isNaN(amountNum) || amountNum <= 0) {
            alert('Amount должен быть больше 0');
            return;
        }

        setLoading(true);
        try {
            const payload = {
                title,
                amount_cents: Math.round(parseFloat(amount) * 100),
                category: category.trim() || "other",
            };
            await createExpense(payload);
            setTitle('');
            setAmount('');
            setCategory('');
            onExpenseAdded();
        } catch (err) {
            // Ошибка уже обработана в api.ts (alert)
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const inputStyle = { margin: '5px', padding: '8px', fontSize: '14px' };

    return (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc' }}>
            <div>
                <input
                    data-testid="title-input"
                    type="text"
                    placeholder="Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    style={inputStyle}
                />
                <label>Сумма (₽)</label>
                <input
                    data-testid="amount-input"
                    type="number"
                    placeholder="Например: 350"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                    min="1"
                    style={inputStyle}
                />
                <input
                    data-testid="category-input"
                    type="text"
                    placeholder="Category (optional)"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    style={inputStyle}
                />
                <button
                    data-testid="add-button"
                    type="submit"
                    disabled={loading}
                    style={{ ...inputStyle, cursor: loading ? 'not-allowed' : 'pointer' }}
                >
                    {loading ? 'Adding...' : 'Add'}
                </button>
            </div>
        </form>
    );
};