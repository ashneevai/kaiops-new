import { test, expect } from "@playwright/test";

test("dashboard renders", async ({ page }) => {
  await page.goto("http://localhost:3000/dashboard");
  await expect(page.getByText("Executive Dashboard")).toBeVisible();
});
