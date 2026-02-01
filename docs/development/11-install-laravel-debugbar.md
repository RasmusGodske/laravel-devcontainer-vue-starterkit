# Laravel Debugbar

## Overview

Laravel Debugbar provides a powerful debugging toolbar that displays real-time insights into your application's performance and behavior. It helps you identify slow queries, track memory usage, inspect routes, and debug request/response data - all without adding `dd()` statements or log entries throughout your code.

## Usage

Debugbar appears automatically as a toolbar at the bottom of your browser when running in development mode. Simply visit any page in your application to see it.

### Available Tabs

The toolbar includes these tabs:

| Tab | What it Shows |
|-----|---------------|
| **Messages** | Custom debug messages logged via `Debugbar::info()` |
| **Timeline** | Request execution timeline with timing breakdowns |
| **Exceptions** | Any exceptions thrown during the request |
| **Views** | Rendered Blade views and their data |
| **Route** | Current route, controller, and middleware |
| **Queries** | All SQL queries with execution time and bindings |
| **Models** | Eloquent models loaded and their counts |
| **Session** | Current session data |
| **Request** | Request headers, cookies, and input data |

### Logging Custom Messages

You can log messages to Debugbar from your code:

```php
use Barryvdh\Debugbar\Facades\Debugbar;

Debugbar::info('User logged in');
Debugbar::warning('Cache miss for key: ' . $key);
Debugbar::error('Payment failed');
```

## Configuration

### Environment Variable

Debugbar is controlled via environment variable in `.env`:

```env
DEBUGBAR_ENABLED=true
```

Set to `false` to disable the toolbar (useful for E2E tests or when it interferes with debugging).

### Configuration File

To customize Debugbar behavior, publish its configuration:

```bash
php artisan vendor:publish --provider="Barryvdh\Debugbar\ServiceProvider"
```

This creates `config/debugbar.php` where you can:
- Enable/disable specific collectors (tabs)
- Configure storage options
- Adjust display settings
