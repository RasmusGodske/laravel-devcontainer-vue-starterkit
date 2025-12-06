<?php

namespace App\Data\Inertia;

use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

#[TypeScript()]
class InertiaQuoteData extends Data
{
    public function __construct(
        public string $message,
        public string $author,
    ) {}
}
