# Laravel Data Package

## Overview

Spatie's [Laravel-Data](https://spatie.be/docs/laravel-data/v4/introduction) package provides type-safe data transfer objects (DTOs) with built-in validation and transformation. Instead of passing around arrays or writing boilerplate validation logic, you define structured Data classes that:

- Validate incoming requests automatically
- Transform data for API responses
- Provide full IDE autocompletion and type safety
- Replace FormRequests with a cleaner, more reusable pattern

## Usage

### Creating a Data Class

Generate a new Data class using Artisan:

```bash
php artisan make:data UserData
```

This creates a class in `app/Data/`:

```php
namespace App\Data;

use Spatie\LaravelData\Data;

class UserData extends Data
{
    public function __construct(
        public string $name,
        public string $email,
        public ?string $phone = null,
    ) {}
}
```

### Using Data Classes in Controllers

Data classes replace FormRequests for validation and typing:

```php
use App\Data\UserData;

class UserController extends Controller
{
    public function store(UserData $data)
    {
        // $data is already validated and typed
        User::create($data->toArray());

        return redirect()->route('users.index');
    }
}
```

### Adding Validation Rules

Use attributes to define validation:

```php
use Spatie\LaravelData\Attributes\Validation\Email;
use Spatie\LaravelData\Attributes\Validation\Max;
use Spatie\LaravelData\Attributes\Validation\Required;

class UserData extends Data
{
    public function __construct(
        #[Required, Max(255)]
        public string $name,

        #[Required, Email]
        public string $email,

        public ?string $phone = null,
    ) {}
}
```

### Transforming Models to Data

Create Data objects from Eloquent models:

```php
// Single model
$userData = UserData::from($user);

// Collection of models
$users = UserData::collect(User::all());
```

### Nested Data Objects

Data classes can contain other Data classes:

```php
class OrderData extends Data
{
    public function __construct(
        public string $order_number,
        public CustomerData $customer,
        /** @var ProductData[] */
        public array $products,
    ) {}
}
```

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `config/data.php` | Package configuration (publish with `php artisan vendor:publish --tag=data-config`) |
| `app/Data/` | Your Data classes |

### Customization

Common configuration options in `config/data.php`:

- **date_format** - Default format for date casting
- **transformers** - Custom transformers for complex types
- **casts** - Global type casts

For most projects, the defaults work well. See the [Laravel Data documentation](https://spatie.be/docs/laravel-data/v4/as-a-resource/from-data-to-resource) for advanced customization.