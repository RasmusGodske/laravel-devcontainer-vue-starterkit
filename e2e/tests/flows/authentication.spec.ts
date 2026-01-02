import { test, expect } from '../../fixtures/base.fixture';

/**
 * Authentication flow tests.
 * Tests that span multiple pages/routes for auth functionality.
 */
test.describe('Authentication Flow', () => {
  test('user can login and access dashboard', async ({ authenticatedPage }) => {
    const { page } = authenticatedPage;

    await page.goto('/dashboard');

    await expect(page).not.toHaveURL(/\/login/);
    await expect(page).toHaveTitle(/Dashboard/);
  });

  test('user can logout', async ({ authenticatedPage }) => {
    const { page, user } = authenticatedPage;

    await page.goto('/dashboard');

    // Click on the user menu dropdown (shows user name)
    await page.getByRole('button', { name: user.name }).click();

    // Click logout in the dropdown menu
    await page.getByRole('menuitem', { name: /log out/i }).click();

    // Should be redirected to homepage or login
    await expect(page).toHaveURL(/\/(login)?$/);
  });
});

test.describe('E2E API Endpoints', () => {
  test('can create and delete test user via API', async ({ testData }) => {
    const user = await testData.createUser({
      name: 'API Test User',
      email: 'api-test@example.com',
    });

    expect(user.id).toBeDefined();
    expect(user.email).toBe('api-test@example.com');
    expect(user.name).toBe('API Test User');
    expect(user.password).toBe('password');

    await testData.deleteUser(user.id);
  });
});
