import { test as base, type Page } from '@playwright/test';
import { ConsoleErrorsCollector, createConsoleErrorsCollector } from './console-errors';
import { type TestUser, createTestDataHelper, TestDataHelper } from './test-data';

/**
 * Extended test fixtures for E2E testing
 */
export interface TestFixtures {
  /**
   * Test data helper for creating/managing test data via API
   */
  testData: TestDataHelper;

  /**
   * Console errors collector for monitoring browser console
   */
  consoleErrors: ConsoleErrorsCollector;

  /**
   * An authenticated page fixture - creates a user, logs in, and provides the page
   */
  authenticatedPage: {
    page: Page;
    user: TestUser;
  };
}

/**
 * Extended test with custom fixtures
 */
export const test = base.extend<TestFixtures>({
  /**
   * Test data helper fixture
   * Automatically available in all tests
   */
  testData: async ({ request }, use) => {
    const helper = createTestDataHelper(request);
    await use(helper);
  },

  /**
   * Console errors collector fixture
   * Automatically attached to the page
   */
  consoleErrors: async ({ page }, use) => {
    const collector = createConsoleErrorsCollector(page);
    await use(collector);
  },

  /**
   * Authenticated page fixture
   * Creates a test user, logs them in, and provides both page and user
   */
  authenticatedPage: async ({ page, request }, use) => {
    const testData = createTestDataHelper(request);

    // Create a test user
    const user = await testData.createUser();

    // Navigate to login page
    await page.goto('/login');

    // Fill in login form
    await page.locator('#email').fill(user.email);
    await page.locator('#password').fill(user.password);

    // Click login button
    await page.getByRole('button', { name: /log in/i }).click();

    // Wait for navigation to complete (redirected away from login)
    await page.waitForURL((url) => !url.pathname.includes('/login'));

    // Provide the authenticated page and user to the test
    await use({ page, user });

    // Cleanup: delete the test user after the test
    await testData.deleteUser(user.id);
  },
});

/**
 * Re-export expect from base
 */
export { expect } from '@playwright/test';
