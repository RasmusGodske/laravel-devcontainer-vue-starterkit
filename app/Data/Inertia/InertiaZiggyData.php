<?php

namespace App\Data\Inertia;

use Illuminate\Http\Request;
use Spatie\LaravelData\Data;
use Spatie\TypeScriptTransformer\Attributes\TypeScript;
use Tighten\Ziggy\Ziggy;

/**
 * Represents the various available Ziggy routes and their configurations.
 * This data structure is used to provide route information to Inertia responses.
 *
 * This is used within resources/js/ssr.ts
 */
#[TypeScript()]
class InertiaZiggyData extends Data
{
    /**
     * @param  string  $url  The base URL for the Ziggy routes.
     * @param  int|null  $port  The port number for the Ziggy routes.
     * @return void
     */
    public function __construct(
        public string $url,
        public ?int $port,
        public array $defaults,
        public array $routes,
        public string $location,
    ) {}

    public static function fromZiggy(
        Ziggy $ziggy,
        Request $request,
    ): self {
        $arrayRepresentation = $ziggy->toArray();

        return new self(
            url: $arrayRepresentation['url'],
            port: $arrayRepresentation['port'],
            defaults: $arrayRepresentation['defaults'],
            routes: $arrayRepresentation['routes'],
            location: $request->url(),
        );
    }
}
