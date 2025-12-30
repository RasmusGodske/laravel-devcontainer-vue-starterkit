import { test, expect } from '../fixtures/base.fixture';

/**
 * Smoke Tests
 *
 * Basic tests to verify the application is running correctly.
 * These should be fast and test core functionality.
 */
test.describe('Smoke Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');

    // Check that the page loads without errors
    await expect(page).toHaveTitle(/Laravel/);
  });

  test('login page is accessible', async ({ page }) => {
    await page.goto('/login');

    // Check that login form elements are present
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.getByRole('button', { name: /log in/i })).toBeVisible();
  });

  test('register page is accessible', async ({ page }) => {
    await page.goto('/register');

    // Check that registration form elements are present
    await expect(page.locator('#name')).toBeVisible();
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
  });

  test('unauthenticated user is redirected from dashboard', async ({ page }) => {
    await page.goto('/dashboard');

    // Should be redirected to login page
    await expect(page).toHaveURL(/\/login/);
  });

  test('no console errors on homepage', async ({ page, consoleErrors }) => {
    await page.goto('/');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');

    // Assert no JavaScript errors occurred
    consoleErrors.assertNoErrors([
      // Ignore known benign errors if any
      /favicon\.ico/,
    ]);
  });
});

test.describe('Authentication Flow', () => {
  test('user can login and access dashboard', async ({ authenticatedPage }) => {
    const { page } = authenticatedPage;

    // Navigate to dashboard
    await page.goto('/dashboard');

    // Should be on dashboard (not redirected to login)
    await expect(page).not.toHaveURL(/\/login/);

    // Page title should contain "Dashboard"
    await expect(page).toHaveTitle(/Dashboard/);
  });

  test('user can logout', async ({ authenticatedPage }) => {
    const { page, user } = authenticatedPage;

    // Navigate to dashboard
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
    // Create a test user
    const user = await testData.createUser({
      name: 'API Test User',
      email: 'api-test@example.com',
    });

    // Verify user was created
    expect(user.id).toBeDefined();
    expect(user.email).toBe('api-test@example.com');
    expect(user.name).toBe('API Test User');
    expect(user.password).toBe('password');

    // Clean up - delete the user
    await testData.deleteUser(user.id);
  });
});
