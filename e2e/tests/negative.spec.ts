import { test, expect } from "./fixtures";

// Конфигурация через переменные окружения (см. e2e/.env.example)
const API_URL = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";

test.describe("негативные сценарии UI @negative", () => {
  test.beforeEach(async ({ expensesPage }) => {
    await expensesPage.goto();
  });

  test("пустой Title показывает сообщение об ошибке в DOM", async ({ expensesPage }) => {
    await expensesPage.amountInput.fill("100");
    await expensesPage.addButton.click();

    await expect(expensesPage.errorMessage).toBeVisible();
    await expect(expensesPage.errorMessage).toContainText("Title не может быть пустым");
    // Расход не создан — список остался пустым
    await expect(expensesPage.expenseRows).toHaveCount(0);
  });

  test("Amount <= 0 показывает сообщение об ошибке", async ({ expensesPage }) => {
    // HTML min="1" блокирует нативную отправку формы,
    // поэтому убираем атрибут и эмулируем невалидный ввод
    await expensesPage.amountInput.evaluate((el) => el.removeAttribute("min"));

    await expensesPage.submitWithInvalidAmount("0");

    await expect(expensesPage.errorMessage).toBeVisible();
    await expect(expensesPage.errorMessage).toContainText("Amount должен быть больше 0");
    await expect(expensesPage.expenseRows).toHaveCount(0);
  });

  test("ошибка сервера 500 при создании расхода отображается в DOM", async ({ page, expensesPage }) => {
    let intercepted = false;

    // Подменяем ответ API на 500 без остановки самого бэкенда
    await page.route(`${API_URL}/api/expenses*`, async (route) => {
      const request = route.request();
      if (request.method() === "POST") {
        intercepted = true;
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Internal Server Error" }),
        });
      } else {
        await route.continue();
      }
    });

    await expensesPage.titleInput.fill(`Server error ${Date.now()}`);
    await expensesPage.amountInput.fill("100");
    await expensesPage.addButton.click();

    await expect(expensesPage.errorMessage).toBeVisible();
    await expect(expensesPage.errorMessage).toContainText("Ошибка сервера (500)");
    expect(intercepted).toBe(true);
  });

  test("сообщение об ошибке скрывается после успешного создания расхода", async ({ page, expensesPage, request }) => {
    // Гарантируем чистый список перед тестом
    const response = await request.get(`${API_URL}/api/expenses`, {
      headers: { "X-API-Key": process.env.E2E_API_KEY ?? "test-key" },
    });
    for (const expense of await response.json()) {
      await request.delete(`${API_URL}/api/expenses/${expense.id}`, {
        headers: { "X-API-Key": process.env.E2E_API_KEY ?? "test-key" },
      });
    }

    const title = `Recover ${Date.now()}`;
    let blockNext = true;

    // Первый POST падает с 422, второй проходит нормально
    await page.route(`${API_URL}/api/expenses`, async (route) => {
      if (route.request().method() === "POST" && blockNext) {
        blockNext = false;
        await route.fulfill({
          status: 422,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Validation error" }),
        });
      } else {
        await route.continue();
      }
    });

    await expensesPage.titleInput.fill(title);
    await expensesPage.amountInput.fill("100");
    await expensesPage.addButton.click();

    await expect(expensesPage.errorMessage).toContainText("Невалидные данные запроса (422)");

    await expensesPage.addButton.click();

    await expect(expensesPage.errorMessage).not.toBeVisible();
    await expensesPage.expectExpenseVisible(title);
  });
});
