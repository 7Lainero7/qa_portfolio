import { test, expect } from "./fixtures";

test.describe("smoke", () => {
  test("страница загружается и форма видима @smoke", async ({ expensesPage }) => {
    await expensesPage.goto();

    await expect(expensesPage.titleInput).toBeVisible();
    await expect(expensesPage.amountInput).toBeVisible();
    await expect(expensesPage.addButton).toBeVisible();
    await expect(expensesPage.expenseList).toBeVisible();
  });
});