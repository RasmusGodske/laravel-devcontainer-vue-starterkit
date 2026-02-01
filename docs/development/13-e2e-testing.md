# E2E Testing with Playwright

## Overview

End-to-end testing ensures your entire application works correctly from a user's perspective. This starterkit includes Playwright for browser-based E2E testing because:

- **Reliable browser automation** - Tests run against real browsers, catching issues unit tests miss
- **Excellent debugging tools** - Visual UI mode, trace viewer, and screenshot/video capture on failures
- **Isolated test environment** - Separate `.env.e2e` configuration prevents test data from polluting development
- **Ready to use** - Testing infrastructure is already configured, so you can start writing tests immediately

## Usage

### Running Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with visible browser
npm run test:e2e:headed

# Open Playwright UI for interactive testing
npm run test:e2e:ui

# Debug mode with inspector
npm run test:e2e:debug

# View HTML report after tests complete
npm run test:e2e:report

# Or use the alias
e2e
```

### Writing Tests

Tests go in `e2e/tests/` and use the `.spec.ts` extension. Import from the base fixture to get access to custom helpers:

```typescript
import { test, expect } from '../fixtures/base.fixture';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/some-page');
    await expect(page.locator('h1')).toHaveText('Expected Title');
  });
});
```

### Using the Authentication Fixture

For tests that require a logged-in user, use the `authenticatedPage` fixture. It automatically creates a test user, logs them in, and cleans up after the test:

```typescript
import { test, expect } from '../fixtures/base.fixture';

test('authenticated user can access dashboard', async ({ authenticatedPage }) => {
  const { page, user } = authenticatedPage;

  await page.goto('/dashboard');
  await expect(page).toHaveTitle(/Dashboard/);

  // user.email, user.name, user.password are available if needed
});
```

### Creating Test Data

Use the `testData` fixture to create users or other test data via the E2E API:

```typescript
import { test, expect } from '../fixtures/base.fixture';

test('admin can see user list', async ({ page, testData }) => {
  // Create test users
  const user1 = await testData.createUser({ name: 'Alice' });
  const user2 = await testData.createUser({ name: 'Bob' });

  // Test your feature...

  // Clean up (optional - database resets between runs)
  await testData.deleteUser(user1.id);
  await testData.deleteUser(user2.id);
});
```

### Checking for Console Errors

Use the `consoleErrors` fixture to verify pages load without JavaScript errors:

```typescript
import { test } from '../fixtures/base.fixture';

test('page loads without errors', async ({ page, consoleErrors }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  // Optionally ignore specific patterns (e.g., known third-party issues)
  consoleErrors.assertNoErrors([/favicon\.ico/]);
});
```

### Common Patterns

**Waiting for navigation:**
```typescript
await page.getByRole('button', { name: 'Submit' }).click();
await page.waitForURL('/success');
```

**Filling forms:**
```typescript
await page.locator('#email').fill('user@example.com');
await page.locator('#password').fill('password');
await page.getByRole('button', { name: /log in/i }).click();
```

**Checking visibility:**
```typescript
await expect(page.getByText('Welcome')).toBeVisible();
await expect(page.locator('.error-message')).not.toBeVisible();
```

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `playwright.config.ts` | Main Playwright configuration (timeouts, browser settings, reporters) |
| `.env.e2e` | Environment configuration for test runs (database, caching, etc.) |
| `e2e/scripts/e2e-server.sh` | Script that starts the Laravel server for tests |
| `e2e/fixtures/base.fixture.ts` | Custom test fixtures (authentication, test data, console errors) |
| `routes/e2e.php` | API routes for test data management |

### Directory Structure

```
e2e/
├── fixtures/
│   ├── base.fixture.ts      # Extended test with custom fixtures
│   ├── test-data.ts         # Test data creation helpers
│   └── console-errors.ts    # Console error collector
├── tests/
│   └── smoke.spec.ts        # Sample smoke tests
├── scripts/
│   └── e2e-server.sh        # Server startup script
└── reports/                 # Generated test reports (gitignored)
```

### Customization

**Adding more browsers:** Edit `playwright.config.ts` to add Firefox or WebKit:

```typescript
projects: [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  { name: 'webkit', use: { ...devices['Desktop Safari'] } },
],
```

**Adjusting timeouts:** Modify the timeout values in `playwright.config.ts`:

```typescript
use: {
  actionTimeout: 10000,      // Max time for actions like click()
  navigationTimeout: 30000,  // Max time for page.goto()
},
timeout: 60000,              // Max time per test
expect: { timeout: 5000 },   // Max time for expect() assertions
```

**Adding E2E API endpoints:** Create new controllers in `app/Http/Controllers/E2E/` and register routes in `routes/e2e.php`. These routes are only available in local and testing environments.
