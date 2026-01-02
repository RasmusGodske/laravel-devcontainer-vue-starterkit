import { test, expect } from '../../../fixtures/base.fixture';
import { createConsoleErrorCollector } from '../../../fixtures/console-errors';

/**
 * Smoke tests for the Dashboard page.
 * Verifies the page loads without errors for authenticated users.
 */
test.describe('Dashboard Page', () => {
  test('page loads without console errors', async ({ authenticatedPage }) => {
    const { page } = authenticatedPage;
    const errorCollector = createConsoleErrorCollector(page);

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveURL(/\/dashboard/);
    expect(errorCollector.getErrors()).toEqual([]);
  });

  test('displays page content', async ({ authenticatedPage }) => {
    const { page } = authenticatedPage;

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveTitle(/Dashboard/);
  });

  test('redirects unauthenticated user to login', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page).toHaveURL(/\/login/);
  });
});
