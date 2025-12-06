<?php

declare(strict_types=1);

use Rector\CodingStyle\Rector\String_\UseClassKeywordForClassNameResolutionRector;
use Rector\Config\RectorConfig;
use Rector\Custom\AppHelperToMakeRector;

return RectorConfig::configure()
    ->withPaths([
        __DIR__.'/app',
    ])
    // Enable automatic import of fully qualified names
    ->withImportNames(
        importNames: true,
        importDocBlockNames: true,  // Also import classes in PHPDoc comments
        importShortClasses: false,
        removeUnusedImports: false  // Let Pint handle this
    )
    // Use the coding style set which includes import rules
    ->withPreparedSets(
        codingStyle: true,  // This enables name importing
        deadCode: false,
        codeQuality: false,
        typeDeclarations: false,
        privatization: false,
        naming: false,
        instanceOf: false,
        earlyReturn: false,
        strictBooleans: false
    )
    // Register custom rules
    ->withRules([
        AppHelperToMakeRector::class,
    ])
    // Skip rules that might interfere with Laravel conventions
    ->withSkip([
        // Skip paths
        __DIR__.'/vendor',
        __DIR__.'/bootstrap',
        __DIR__.'/storage',
        __DIR__.'/database',
        // __DIR__.'/tests',

        // Skip specific rules that might cause issues
        UseClassKeywordForClassNameResolutionRector::class,
    ]);
