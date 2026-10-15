import { test as base } from "@playwright/test";
import { ExpensesPage } from "../pages/ExpensesPage";

type Fixtures = {
  expensesPage: ExpensesPage;
};

export const test = base.extend<Fixtures>({
  expensesPage: async ({ page }, use) => {
    const expensesPage = new ExpensesPage(page);
    await use(expensesPage);
  },
});

export { expect } from "@playwright/test";