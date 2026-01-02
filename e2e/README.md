# E2E Testing with Playwright

This project uses [Playwright](https://playwright.dev/) for end-to-end testing.

## Setup

1. Install Playwright and its browsers:

```bash
npm install
npx playwright install
```

2. Ensure the E2E environment file exists:

```bash
# The .env.e2e file should already exist. If not:
cp .env.example .env.e2e
# Then update .env.e2e for testing (SQLite, array sessions, etc.)
```

## Running Tests

### Basic Commands

```bash
# Run all E2E tests
npm run test:e2e

# Run tests with headed browser (visible)
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug

# Open Playwright UI for interactive testing
npm run test:e2e:ui

# View the HTML report
npm run test:e2e:report
```

### Running Specific Tests

```bash
# Run a specific test file
npx playwright test e2e/tests/routes/login/smoke.spec.ts

# Run tests matching a pattern
npx playwright test --grep "login"

# Run tests in a specific project (browser)
npx playwright test --project=chromium
```

## Project Structure

```
e2e/
├── fixtures/                    # Test fixtures and helpers
│   ├── base.fixture.ts          # Extended test with custom fixtures
│   ├── test-data.ts             # Test data creation helpers
│   └── console-errors.ts        # Console error collector
├── tests/
│   ├── routes/                  # Route-based tests (validated by hook)
│   │   ├── login/
│   │   │   └── smoke.spec.ts
│   │   ├── register/
│   │   │   └── smoke.spec.ts
│   │   └── dashboard/
│   │       └── smoke.spec.ts
│   └── flows/                   # Multi-page user flows
│       └── authentication.spec.ts
├── scripts/
│   └── e2e-server.sh            # Server startup script
├── reports/                     # Test reports (gitignored)
│   ├── html/                    # HTML report
│   └── test-results/            # Test artifacts
└── README.md                    # This file
```

### Route-Based Test Structure

Tests in `e2e/tests/routes/` must mirror Laravel routes exactly:

```
Laravel Route          →    Test Directory
GET /login             →    e2e/tests/routes/login/
GET /register          →    e2e/tests/routes/register/
GET /dashboard         →    e2e/tests/routes/dashboard/
GET /app/users         →    e2e/tests/routes/app/users/index/
```

**Important:** The E2EPathValidator hook validates that test paths correspond to actual Laravel routes.

### Non-Route Tests

Tests that don't correspond to specific routes go in other directories:

- `flows/` - Multi-page user flows (login → dashboard → logout)
- `api/` - API-only tests
- `components/` - Isolated component tests

## Fixtures

### testData

Helper for creating and managing test data via the E2E API:

```typescript
test('example', async ({ testData }) => {
  // Create a test user
  const user = await testData.createUser({
    name: 'Test User',
    email: 'test@example.com',
  });

  // Use the user in your test...

  // Clean up (automatic with authenticatedPage fixture)
  await testData.deleteUser(user.id);
});
```

### authenticatedPage

Pre-authenticated page with a test user:

```typescript
test('dashboard access', async ({ authenticatedPage }) => {
  const { page, user } = authenticatedPage;

  // Page is already logged in as user
  await page.goto('/dashboard');
  await expect(page).not.toHaveURL(/\/login/);

  // User cleanup happens automatically after the test
});
```

### consoleErrors

Collects and asserts on browser console errors:

```typescript
test('no console errors', async ({ page, consoleErrors }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  // Assert no errors (with optional ignore patterns)
  consoleErrors.assertNoErrors([
    /favicon\.ico/, // Ignore favicon errors
  ]);
});
```

## E2E API Endpoints

The application exposes E2E-only endpoints when running in local/testing environment:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/e2e/users` | POST | Create a test user |
| `/e2e/users/{id}` | DELETE | Delete a test user |

These endpoints are only available when `APP_ENV=local` or `APP_ENV=testing`.

## Configuration

### playwright.config.ts

Key settings:
- **baseURL**: `http://localhost:8081` (E2E server port)
- **webServer**: Automatically starts the E2E server before tests
- **testDir**: `./e2e/tests`
- **reporters**: HTML and list reporters

### .env.e2e

Key differences from `.env`:
- `APP_ENV=testing`
- `DB_CONNECTION=sqlite` with in-memory database
- `SESSION_DRIVER=array`
- `CACHE_STORE=array`
- `BCRYPT_ROUNDS=4` (faster password hashing for tests)

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '../fixtures/base.fixture';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/some-page');
    await expect(page.getByText('Expected Text')).toBeVisible();
  });
});
```

### Best Practices

1. **Use fixtures for authentication** - Don't manually log in each test
2. **Clean up test data** - Use the `testData` fixture and clean up after tests
3. **Assert on console errors** - Use `consoleErrors.assertNoErrors()` in critical tests
4. **Use meaningful selectors** - Prefer `getByRole`, `getByText` over CSS selectors
5. **Wait for network** - Use `waitForLoadState('networkidle')` when needed

### Example: Authenticated Feature Test

```typescript
import { test, expect } from '../fixtures/base.fixture';

test.describe('User Profile', () => {
  test('can update profile', async ({ authenticatedPage, consoleErrors }) => {
    const { page, user } = authenticatedPage;

    // Navigate to profile
    await page.goto('/profile');

    // Update name
    await page.locator('#name').fill('Updated Name');
    await page.getByRole('button', { name: /save/i }).click();

    // Verify success
    await expect(page.getByText('Profile updated')).toBeVisible();

    // No console errors
    consoleErrors.assertNoErrors();
  });
});
```

## CI/CD Integration

For CI environments, set `CI=true`:

```bash
CI=true npm run test:e2e
```

This enables:
- No retries in parallel mode
- Single worker
- Fail on `test.only` in source code

## Troubleshooting

### Server not starting

```bash
# Check if the server script is executable
chmod +x e2e/scripts/e2e-server.sh

# Try starting manually
bash e2e/scripts/e2e-server.sh start
```

### Tests timing out

1. Increase timeout in `playwright.config.ts`
2. Check if the server is actually running on port 8081
3. Check the `.env.e2e` configuration

### Database issues

Ensure SQLite is configured in `.env.e2e`:

```env
DB_CONNECTION=sqlite
DB_DATABASE=:memory:
```

### Browser installation

```bash
npx playwright install
```
