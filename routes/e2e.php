<?php

use App\Http\Controllers\E2E\UserController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| E2E Testing Routes
|--------------------------------------------------------------------------
|
| These routes are ONLY available in local and testing environments.
| They provide endpoints for Playwright E2E tests to create and clean up
| test data using Laravel factories.
|
| IMPORTANT: These routes are NOT available in production.
|
*/

Route::prefix('e2e')->group(function () {
    // User management
    Route::post('/users', [UserController::class, 'store']);
    Route::delete('/users/{user}', [UserController::class, 'destroy']);
});
