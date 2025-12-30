<?php

namespace App\Http\Controllers\E2E;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

/**
 * E2E test controller for User management.
 *
 * IMPORTANT: Only available in local and testing environments.
 */
class UserController extends Controller
{
    /**
     * Create a user for E2E testing.
     *
     * POST /e2e/users
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'email' => 'sometimes|email|max:255',
        ]);

        // Generate unique email if not provided
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
            'password' => 'password', // Plain text for E2E tests
        ], 201);
    }

    /**
     * Delete a user.
     *
     * DELETE /e2e/users/{user}
     */
    public function destroy(User $user): JsonResponse
    {
        $user->forceDelete();

        return response()->json([
            'message' => 'User deleted successfully',
        ]);
    }
}
