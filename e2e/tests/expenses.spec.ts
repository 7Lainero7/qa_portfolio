import { test, expect } from "./fixtures";

test.describe("расходы", () => {
  test.beforeEach(async ({ expensesPage }) => {
    await expensesPage.goto();
  });

  test("создание расхода добавляет его в список @smoke", async ({ expensesPage }) => {
    const title = `E2E Coffee ${Date.now()}`;

    await expensesPage.addExpense(title, 35000, "food");

    await expensesPage.expectExpenseVisible(title);
  });

  test("создание нескольких расходов сохраняет порядок (новые сверху)", async ({ expensesPage }) => {
    const title1 = `First ${Date.now()}`;
    const title2 = `Second ${Date.now()}`;

    await expensesPage.addExpense(title1, 10000, "food");
    await expensesPage.addExpense(title2, 20000, "transport");

    const titles = await expensesPage.getExpenseTitles();

    // Новые сверху → title2 должен быть раньше title1
    expect(titles.indexOf(title2)).toBeLessThan(titles.indexOf(title1));
  });

  test("удаление расхода убирает его из списка @smoke", async ({ expensesPage }) => {
    const title = `To delete ${Date.now()}`;

    await expensesPage.addExpense(title, 5000, "other");
    await expensesPage.expectExpenseVisible(title);

    await expensesPage.deleteExpenseByTitle(title);
    await expensesPage.expectExpenseNotVisible(title);
  });
});