<?php

/**
 * Typescript Transformer used by the package: "spatie/typescript-transformer" to generate TypeScript definitions
 * from PHP classes.
 *
 * This specific one is a custom transformer mainly created/inspired from github.com/nolanos
 *
 * @see https://github.com/nolanos/laravel-model-typescript-transfomer/blob/main/src/ModelTransformer.php
 */

namespace App\TypescriptTransformers;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Schema;
use ReflectionClass;
use Spatie\TypeScriptTransformer\Structures\TransformedType;
use Spatie\TypeScriptTransformer\Transformers\Transformer;

class EloquentModelTransformer implements Transformer
{
    public function transform(ReflectionClass $class, string $name): ?TransformedType
    {
        if (! is_subclass_of($class->name, Model::class)) {
            return null;
        }
        /** @var Model $modelInstance */
        $modelInstance = $class->newInstanceWithoutConstructor();

        $table = $modelInstance->getTable();

        $hidden = $modelInstance->getHidden();
        $casts = $modelInstance->getCasts();
        $appends = $modelInstance->getAppends();

        $columns = Schema::getColumns($table);
        $columnNames = array_map(fn ($col) => $col['name'], $columns);

        $serializedColumnNames = array_diff($columnNames, $hidden);

        $typescriptProperties = [];

        foreach ($serializedColumnNames as $index => $propertyName) {
            $column = $columns[$index];
            $isNullable = $column['nullable'];

            if (array_key_exists($propertyName, $casts)) {
                $typescriptType = $this->mapCastToType($casts[$propertyName]);
            } else {
                $typescriptType = $this->mapTypeNameToJsonType($column['type_name']);
            }

            $typescriptPropertyDefinition = "$propertyName: $typescriptType";

            if ($isNullable) {
                $typescriptPropertyDefinition .= ' | null';
            }

            $typescriptProperties[] = $typescriptPropertyDefinition;
        }

        foreach ($appends as $append) {
            $type = 'any';
            if ($comment = $class->getDocComment()) {
                $matches = [];
                $regex = '/@property\s+([^\s]+)\s+\$'.$append.'\s*\n/';

                preg_match($regex, $comment, $matches);

                // dump($comment, $append, $regex, $matches);

                if (count($matches) > 1) {
                    $type = $this->mapCastToType($matches[1]);
                }
            }

            $typescriptProperties[] = "$append: $type";
        }

        // Add relation types
        $relationProperties = $this->getRelationProperties($class, $modelInstance);
        $typescriptProperties = array_merge($typescriptProperties, $relationProperties);

        return TransformedType::create(
            $class,
            $name,
            "{\n".implode("\n", $typescriptProperties)."\n}",
        );
    }

    private function mapTypeNameToJsonType(string $columnType): string
    {
        // Map Laravel column types to TypeScript types
        return match ($columnType) {
            // Strings
            'uuid', 'string', 'text', 'varchar', 'character varying', 'date', 'datetime', 'timestamp', 'timestamp without time zone', 'bpchar', 'timestamptz', 'time', 'bytea', 'blob' => 'string',
            // Numbers
            'integer', 'bigint', 'int2', 'int4', 'int8', 'float', 'double', 'decimal', 'float8', 'numeric' => 'number',
            // Booleans
            'boolean', 'bool' => 'boolean',
            // Unknown
            default => 'unknown /* '.$columnType.' */', // Fallback for other types
        };
    }

    private function mapCastToType(string $cast): string
    {
        if (enum_exists($cast)) {
            return implode(' | ', array_map(fn ($case) => "'$case->value'", $cast::cases()));
        }

        return match ($cast) {
            'boolean', 'bool' => 'boolean',
            'int', 'float' => 'number',
            'string', 'datetime', 'timestamp', 'date', 'uuid' => 'string',
            'array', 'object' => 'any',
            'collection' => 'any[]',
            default => 'unknown /* '.$cast.' */',
        };
    }

    private function getRelationProperties(ReflectionClass $class, Model $modelInstance): array
    {
        $relationProperties = [];

        // Parse PHPDoc comments to extract relation information
        $docComment = $class->getDocComment();
        if ($docComment) {
            $relationProperties = $this->parseRelationsFromDocComment($docComment);
        }

        return $relationProperties;
    }

    private function parseRelationsFromDocComment(string $docComment): array
    {
        $relationProperties = [];

        // Match @property-read patterns for relations
        // Example: @property-read \Illuminate\Database\Eloquent\Collection|\App\Models\ObjectDefinitionColumn[] $columns
        // Example: @property-read \App\Models\Customer|null $customer
        preg_match_all('/@property-read\s+([^$\s]+)\s+\$(\w+)/m', $docComment, $matches, PREG_SET_ORDER);

        foreach ($matches as $match) {
            $typeDeclaration = $match[1];
            $propertyName = $match[2];

            // Skip count properties (e.g., columns_count)
            if (str_ends_with($propertyName, '_count')) {
                continue;
            }

            $typescriptType = $this->parseRelationTypeFromDocComment($typeDeclaration);
            if ($typescriptType !== null) {
                $relationProperties[] = "$propertyName?: $typescriptType";
            }
        }

        return $relationProperties;
    }

    private function parseRelationTypeFromDocComment(string $typeDeclaration): ?string
    {
        // Handle Collection types: \Illuminate\Database\Eloquent\Collection|\App\Models\Model[]
        if (preg_match('/\\\\Illuminate\\\\Database\\\\Eloquent\\\\Collection\\\\([^\\\\]+)(\\\\.+)?\\[\\]/', $typeDeclaration, $matches)) {
            $modelClass = $matches[1].($matches[2] ?? '');

            // Check if the model class has TypeScript attribute
            if (! $this->hasTypeScriptAttribute($modelClass)) {
                return 'any[]';
            }

            $typescriptNamespace = $this->convertNamespaceToTypescript($modelClass);

            return "{$typescriptNamespace}[]";
        }

        // Handle simple model types: \App\Models\Customer|null or \App\Models\Data\DataObject
        if (preg_match('/\\\\App\\\\Models\\\\([^|\\s]+)/', $typeDeclaration, $matches)) {
            $modelPath = $matches[1];
            $fullModelClass = "App\\Models\\{$modelPath}";

            // Check if the model class has TypeScript attribute
            if (! $this->hasTypeScriptAttribute($fullModelClass)) {
                return str_contains($typeDeclaration, '|null') ? 'any | null' : 'any';
            }

            $typescriptNamespace = 'App.Models.'.str_replace('\\', '.', $modelPath);

            // Check if nullable
            if (str_contains($typeDeclaration, '|null')) {
                return "$typescriptNamespace | null";
            }

            return $typescriptNamespace;
        }

        return null;
    }

    private function hasTypeScriptAttribute(string $className): bool
    {
        if (! class_exists($className)) {
            return false;
        }

        $reflection = new ReflectionClass($className);
        $attributes = $reflection->getAttributes();

        foreach ($attributes as $attribute) {
            if ($attribute->getName() === 'Spatie\\TypeScriptTransformer\\Attributes\\TypeScript') {
                return true;
            }
        }

        return false;
    }

    private function convertNamespaceToTypescript(string $phpNamespace): string
    {
        // Convert App\Models\Data\DataObject to App.Models.Data.DataObject
        return str_replace('\\', '.', $phpNamespace);
    }
}
