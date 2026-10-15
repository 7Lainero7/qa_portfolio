import { type Page, type Locator, expect } from "@playwright/test";

export class ExpensesPage {
  readonly page: Page;
  readonly titleInput: Locator;
  readonly amountInput: Locator;
  readonly categoryInput: Locator;
  readonly addButton: Locator;
  readonly expenseList: Locator;
  readonly expenseRows: Locator;

  constructor(page: Page) {
    this.page = page;
    this.titleInput = page.getByTestId("title-input");
    this.amountInput = page.getByTestId("amount-input");
    this.categoryInput = page.getByTestId("category-input");
    this.addButton = page.getByTestId("add-button");
    this.expenseList = page.getByTestId("expense-list");
    this.expenseRows = page.getByTestId("expense-row");
  }

  async goto() {
    await this.page.goto("/");
    await this.expenseList.waitFor({ state: "visible" });
  }

  async addExpense(title: string, amountCents: number, category?: string) {
    await this.titleInput.fill(title);
    await this.amountInput.fill(amountCents.toString());

    if (category) {
      await this.categoryInput.fill(category);
    }

    await this.addButton.click();

    // 🔥 КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Ждем, пока строка с этим заголовком реально появится в DOM.
    // Это синхронизирует скорость Playwright со скоростью обновления React.
    await this.expectExpenseVisible(title);
  }

  async getRowsTextContents(): Promise<string[]> {
    return this.expenseRows.allTextContents();
  }

  async countExpenses(): Promise<number> {
    return this.expenseRows.count();
  }

  async deleteExpenseByTitle(title: string) {
    const row = this.expenseRows.filter({ hasText: title });
    await row.getByTestId("delete-button").click();

    // То же самое для удаления: ждем, пока строка исчезнет
    await this.expectExpenseNotVisible(title);
  }

  async expectExpenseVisible(title: string) {
    const row = this.expenseRows.filter({ hasText: title });
    await expect(row).toBeVisible();
  }

  async expectExpenseNotVisible(title: string) {
    const row = this.expenseRows.filter({ hasText: title });
    await expect(row).toHaveCount(0);
  }
}