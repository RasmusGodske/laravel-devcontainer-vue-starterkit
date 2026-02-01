# E2E Testing with Playwright

## Why This Step
End-to-end testing ensures the entire application works correctly from a user's perspective. Playwright provides reliable browser automation with excellent debugging tools and cross-browser support. Having E2E testing boilerplate in the starterkit means new projects start with testing infrastructure already in place.

## What It Does
- Installs Playwright for browser-based E2E testing
- Creates isolated test environment (separate `.env.e2e` configuration)
- Provides E2E API endpoints for test data management
- Sets up fixtures for authentication and error collection
- Configures automatic server startup during tests
- Adds devcontainer support with browser dependencies

## Implementation

### 1. Install Playwright

Add Playwright to devDependencies in `package.json`:

```json
{
  "devDependencies": {
    "@playwright/test": "^1.49.1"
  },
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:report": "playwright show-report e2e/reports/html"
  }
}
```

Then run:
```bash
npm install
npx playwright install chromium
```

### 2. Create E2E Environment File

Create `.env.e2e` with test-specific configuration:

```env
APP_NAME="Laravel E2E"
APP_ENV=testing
APP_KEY=base64:YOUR_KEY_HERE
APP_DEBUG=true
APP_URL=http://localhost:8081

# Use SQLite for isolated, fast tests
DB_CONNECTION=sqlite
DB_DATABASE=:memory:

# Use array-based drivers for speed
SESSION_DRIVER=array
CACHE_STORE=array
QUEUE_CONNECTION=sync

# Faster password hashing for tests
BCRYPT_ROUNDS=4

MAIL_MAILER=log
```

Generate the app key:
```bash
php artisan key:generate --env=e2e
```

### 3. Create E2E API Routes

Create `routes/e2e.php`:

```php
<?php

use App\Http\Controllers\E2E\UserController;
use Illuminate\Support\Facades\Route;

Route::prefix('e2e')->group(function () {
    // User management
    Route::post('/users', [UserController::class, 'store']);
    Route::delete('/users/{user}', [UserController::class, 'destroy']);
});
```

### 4. Register E2E Routes Conditionally

In `routes/web.php`, add at the end:

```php
// E2E Testing routes - ONLY available in local and testing environments
if (app()->isLocal() || app()->environment('testing')) {
    require __DIR__.'/e2e.php';
}
```

### 5. Exclude E2E Routes from CSRF Verification

In `bootstrap/app.php`, add CSRF exception:

```php
->withMiddleware(function (Middleware $middleware) {
    // ... other middleware configuration ...

    // Exclude E2E testing routes from CSRF verification
    $middleware->validateCsrfTokens(except: [
        'e2e/*',
    ]);
})
```

### 6. Create E2E User Controller

Create `app/Http/Controllers/E2E/UserController.php`:

```php
<?php

namespace App\Http\Controllers\E2E;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class UserController extends Controller
{
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'email' => 'sometimes|email|max:255',
        ]);

        $email = $validated['email'] ?? 'e2e-'.strtolower(Str::random(12)).'@test.localhost';

        $user = User::factory()->create([
            'name' => $validated['name'] ?? 'E2E Test User',
            'email' => $email,
            'password' => bcrypt('password'),
            'email_verified_at' => now(),
        ]);

        return response()->json([
            'id' => $user->id,
            'email' => $user->email,
            'name' => $user->name,
            'password' => 'password',
        ], 201);
    }

    public function destroy(User $user): JsonResponse
    {
        $user->forceDelete();

        return response()->json([
            'message' => 'User deleted successfully',
        ]);
    }
}
```

### 7. Create Playwright Configuration

Create `playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: [
    ['html', { outputFolder: 'e2e/reports/html', open: 'never' }],
    ['list'],
  ],

  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:8081',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  timeout: 60000,
  expect: { timeout: 5000 },
  outputDir: 'e2e/reports/test-results',

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'bash e2e/scripts/e2e-server.sh start',
    url: 'http://localhost:8081',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### 8. Create Server Startup Script

Create `e2e/scripts/e2e-server.sh`:

```bash
#!/bin/bash
set -e

PORT=${E2E_PORT:-8081}
HOST=${E2E_HOST:-127.0.0.1}
ENV_FILE=".env.e2e"
PID_FILE="/tmp/e2e-server.pid"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

stop_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            sleep 1
            kill -0 "$PID" 2>/dev/null && kill -9 "$PID" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
}

start_server() {
    # Generate app key if needed
    if grep -q "APP_KEY=$" "$ENV_FILE" 2>/dev/null; then
        php artisan key:generate --env=e2e --force
    fi

    # Run migrations
    php artisan migrate:fresh --env=e2e --force --seed 2>/dev/null || php artisan migrate:fresh --env=e2e --force

    stop_server

    php artisan serve --env=e2e --host="$HOST" --port="$PORT" &
    echo $! > "$PID_FILE"

    # Wait for server
    for i in {1..30}; do
        curl -s "http://$HOST:$PORT" > /dev/null 2>&1 && return 0
        sleep 1
    done
    return 1
}

case "${1:-start}" in
    start) start_server ;;
    stop) stop_server ;;
    restart) stop_server; start_server ;;
esac
```

Make it executable:
```bash
chmod +x e2e/scripts/e2e-server.sh
```

### 9. Create Test Fixtures

Create the E2E directory structure:
```bash
mkdir -p e2e/fixtures e2e/tests e2e/scripts
```

Create `e2e/fixtures/test-data.ts`:

```typescript
import type { APIRequestContext } from '@playwright/test';

export interface TestUser {
  id: number;
  email: string;
  name: string;
  password: string;
}

export class TestDataHelper {
  constructor(private request: APIRequestContext) {}

  async createUser(options?: { name?: string; email?: string }): Promise<TestUser> {
    const response = await this.request.post('/e2e/users', {
      data: { name: options?.name, email: options?.email },
    });
    if (!response.ok()) {
      throw new Error(`Failed to create user: ${response.status()}`);
    }
    return response.json();
  }

  async deleteUser(userId: number): Promise<void> {
    await this.request.delete(`/e2e/users/${userId}`);
  }
}

export function createTestDataHelper(request: APIRequestContext): TestDataHelper {
  return new TestDataHelper(request);
}
```

Create `e2e/fixtures/console-errors.ts`:

```typescript
import type { ConsoleMessage, Page } from '@playwright/test';

export class ConsoleErrorsCollector {
  private messages: { type: string; text: string }[] = [];

  constructor(private page: Page) {
    page.on('console', (msg: ConsoleMessage) => {
      this.messages.push({ type: msg.type(), text: msg.text() });
    });
  }

  getErrors() {
    return this.messages.filter((m) => m.type === 'error');
  }

  assertNoErrors(ignorePatterns: RegExp[] = []): void {
    const errors = this.getErrors().filter(
      (e) => !ignorePatterns.some((p) => p.test(e.text))
    );
    if (errors.length > 0) {
      throw new Error(`Console errors:\n${errors.map((e) => e.text).join('\n')}`);
    }
  }
}

export function createConsoleErrorsCollector(page: Page): ConsoleErrorsCollector {
  return new ConsoleErrorsCollector(page);
}
```

Create `e2e/fixtures/base.fixture.ts`:

```typescript
import { test as base, type Page } from '@playwright/test';
import { ConsoleErrorsCollector, createConsoleErrorsCollector } from './console-errors';
import { type TestUser, createTestDataHelper, TestDataHelper } from './test-data';

export interface TestFixtures {
  testData: TestDataHelper;
  consoleErrors: ConsoleErrorsCollector;
  authenticatedPage: { page: Page; user: TestUser };
}

export const test = base.extend<TestFixtures>({
  testData: async ({ request }, use) => {
    await use(createTestDataHelper(request));
  },

  consoleErrors: async ({ page }, use) => {
    await use(createConsoleErrorsCollector(page));
  },

  authenticatedPage: async ({ page, request }, use) => {
    const testData = createTestDataHelper(request);
    const user = await testData.createUser();

    await page.goto('/login');
    await page.locator('#email').fill(user.email);
    await page.locator('#password').fill(user.password);
    await page.getByRole('button', { name: /log in/i }).click();
    await page.waitForURL((url) => !url.pathname.includes('/login'));

    await use({ page, user });

    await testData.deleteUser(user.id);
  },
});

export { expect } from '@playwright/test';
```

### 10. Create Sample Tests

Create `e2e/tests/smoke.spec.ts`:

```typescript
import { test, expect } from '../fixtures/base.fixture';

test.describe('Smoke Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Laravel/);
  });

  test('login page is accessible', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
  });

  test('no console errors on homepage', async ({ page, consoleErrors }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    consoleErrors.assertNoErrors([/favicon\.ico/]);
  });
});

test.describe('Authentication Flow', () => {
  test('user can login and access dashboard', async ({ authenticatedPage }) => {
    const { page } = authenticatedPage;
    await page.goto('/dashboard');
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page).toHaveTitle(/Dashboard/);
  });
});
```

### 11. Update .gitignore

Add to `.gitignore`:

```
# E2E Testing
/e2e/reports/
/playwright-report/
/test-results/
```

### 12. Update Devcontainer

Add Playwright browser dependencies to `.devcontainer/Dockerfile`:

```dockerfile
# Install Playwright browser dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0
```

Add to `.devcontainer/postCreateCommand.sh` after npm install:

```bash
# Install Playwright browsers if @playwright/test is a dependency
if grep -q "@playwright/test" /home/vscode/project/package.json; then
    echo "Playwright found, installing browsers..."
    npx playwright install chromium
fi
```

Add `e2e` alias to `.devcontainer/Dockerfile`:

```dockerfile
RUN echo "alias e2e='npm run test:e2e'" >> /home/vscode/.zshrc
```

## Directory Structure

After implementation:

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
└── README.md                # E2E documentation
```

## Running Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with visible browser
npm run test:e2e:headed

# Open Playwright UI for interactive testing
npm run test:e2e:ui

# Debug mode with inspector
npm run test:e2e:debug

# View HTML report
npm run test:e2e:report

# Or use the alias
e2e
```

## Key Design Decisions

1. **Separate environment file** (`.env.e2e`) - Isolates test configuration from development
2. **SQLite in-memory** - Fast, isolated database for each test run
3. **E2E API endpoints** - Test data created through Laravel for database consistency
4. **CSRF exception** - E2E routes need to work without browser session
5. **Conditional route loading** - E2E endpoints only available in local/testing
6. **Automatic server startup** - Playwright starts the test server automatically
7. **Fixtures pattern** - Reusable authentication and data creation helpers
