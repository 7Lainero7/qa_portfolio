import { test, expect } from "./fixtures";

// Конфигурация через переменные окружения (см. e2e/.env.example)
const API_URL = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";
const API_KEY = process.env.E2E_API_KEY ?? "test-key";

test.describe("расходы", () => {
  // Очищаем базу перед каждым тестом через API
  test.beforeEach(async ({ expensesPage, request }) => {
    // 1. Делаем запрос к API, чтобы получить все текущие расходы
    const response = await request.get(`${API_URL}/api/expenses`, {
      headers: { "X-API-Key": API_KEY },
    });
    const expenses = await response.json();

    // 2. Удаляем каждый расход по ID
    for (const expense of expenses) {
      await request.delete(`${API_URL}/api/expenses/${expense.id}`, {
        headers: { "X-API-Key": API_KEY },
      });
    }

    // 3. Открываем страницу, теперь она гарантированно пустая
    await expensesPage.goto();
  });

  test("создание расхода добавляет его в список @smoke", async ({ expensesPage }) => {
    const title = `E2E Coffee ${Date.now()}`;

    await expensesPage.addExpense(title, 35000, "food");

    await expensesPage.expectExpenseVisible(title);
    await expect(expensesPage.expenseRows).toHaveCount(1);
  });

  test("создание нескольких расходов сохраняет порядок (новые сверху)", async ({ expensesPage }) => {
    const title1 = `First ${Date.now()}`;
    const title2 = `Second ${Date.now()}`;

    await expensesPage.addExpense(title1, 10000, "food");
    await expensesPage.addExpense(title2, 20000, "transport");

    // Теперь здесь точно будет 2, потому что мы всё почистили в beforeEach
    await expect(expensesPage.expenseRows).toHaveCount(2);

    const rowsText = await expensesPage.getRowsTextContents();

    // rowsText[0] — первая строка (самая новая, title2)
    // rowsText[1] — вторая строка (старая, title1)
    expect(rowsText[0]).toContain(title2);
    expect(rowsText[1]).toContain(title1);
  });

  test("удаление расхода убирает его из списка @smoke", async ({ expensesPage }) => {
    const title = `To delete ${Date.now()}`;

    await expensesPage.addExpense(title, 5000, "other");
    await expect(expensesPage.expenseRows).toHaveCount(1);
    await expensesPage.expectExpenseVisible(title);

    await expensesPage.deleteExpenseByTitle(title);

    await expensesPage.expectExpenseNotVisible(title);
    await expect(expensesPage.expenseRows).toHaveCount(0);
  });
});