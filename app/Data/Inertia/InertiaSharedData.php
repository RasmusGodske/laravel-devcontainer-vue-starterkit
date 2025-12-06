<?php

namespace App\Data\Inertia;

use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;

/**
 * Represents Shared data that is accessible for all Inertia respoonses and is returned by the `HandleInertiaRequests` middleware.
 *
 * @see https://inertiajs.com/shared-data
 */
#[TypeScript()]
class InertiaSharedData extends Data
{
    public function __construct(
        public string $name,
        public InertiaQuoteData $quote,
        public InertiaZiggyData $ziggy,
        public bool $sidebarOpen,
        public object $errors,
        public ?InertiaAuthData $auth = null,
    ) {}
}
