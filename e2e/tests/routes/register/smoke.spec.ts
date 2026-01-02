import { test, expect } from '../../../fixtures/base.fixture';
import { createConsoleErrorCollector } from '../../../fixtures/console-errors';

/**
 * Smoke tests for the Register page.
 * Verifies the page loads without errors and basic elements are present.
 */
test.describe('Register Page', () => {
  test('page loads without console errors', async ({ page }) => {
    const errorCollector = createConsoleErrorCollector(page);

    await page.goto('/register');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveURL(/\/register/);
    expect(errorCollector.getErrors()).toEqual([]);
  });

  test('displays registration form elements', async ({ page }) => {
    await page.goto('/register');

    await expect(page.locator('#name')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
  });
});
