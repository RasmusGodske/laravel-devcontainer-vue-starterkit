import { test, expect } from '../../../fixtures/base.fixture';
import { createConsoleErrorCollector } from '../../../fixtures/console-errors';

/**
 * Smoke tests for the Login page.
 * Verifies the page loads without errors and basic elements are present.
 */
test.describe('Login Page', () => {
  test('page loads without console errors', async ({ page }) => {
    const errorCollector = createConsoleErrorCollector(page);

    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveURL(/\/login/);
    expect(errorCollector.getErrors()).toEqual([]);
  });

  test('displays login form elements', async ({ page }) => {
    await page.goto('/login');

    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.getByRole('button', { name: /log in/i })).toBeVisible();
  });
});
