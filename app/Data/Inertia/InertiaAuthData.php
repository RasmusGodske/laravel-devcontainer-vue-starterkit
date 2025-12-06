<?php

namespace App\Data\Inertia;

use App\Models\User;
use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

#[TypeScript()]
class InertiaAuthData extends Data
{
    public function __construct(
        public User $user,
    ) {}
}
