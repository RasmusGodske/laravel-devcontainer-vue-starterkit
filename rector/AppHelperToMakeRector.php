<?php

declare(strict_types=1);

namespace Rector\Custom;

use PhpParser\Node;
use PhpParser\Node\Expr\ClassConstFetch;
use PhpParser\Node\Expr\FuncCall;
use PhpParser\Node\Expr\MethodCall;
use PhpParser\Node\Name;
use Rector\Rector\AbstractRector;
use Symplify\RuleDocGenerator\ValueObject\CodeSample\CodeSample;
use Symplify\RuleDocGenerator\ValueObject\RuleDefinition;

/**
 * Converts app(Service::class) to app()->make(Service::class)
 * to preserve type information for IDEs and static analysis tools.
 */
final class AppHelperToMakeRector extends AbstractRector
{
    public function getRuleDefinition(): RuleDefinition
    {
        return new RuleDefinition(
            'Convert app(Service::class) to app()->make(Service::class) for better type inference',
            [
                new CodeSample(
                    <<<'CODE_SAMPLE'
$service = app(MyService::class);
CODE_SAMPLE
                    ,
                    <<<'CODE_SAMPLE'
$service = app()->make(MyService::class);
CODE_SAMPLE
                ),
            ]
        );
    }

    /**
     * @return array<class-string<Node>>
     */
    public function getNodeTypes(): array
    {
        return [FuncCall::class];
    }

    /**
     * @param  FuncCall  $node
     */
    public function refactor(Node $node): ?Node
    {
        // Only process app() function calls
        if (! $this->isName($node->name, 'app')) {
            return null;
        }

        // Must have exactly one argument
        if (count($node->args) !== 1) {
            return null;
        }

        $firstArg = $node->args[0];

        // Argument must be a class constant fetch (SomeClass::class)
        if (! $firstArg->value instanceof ClassConstFetch) {
            return null;
        }

        // Transform app(Service::class) into app()->make(Service::class)
        $appCall = new FuncCall(new Name('app'));

        return new MethodCall(
            $appCall,
            'make',
            [$firstArg]
        );
    }
}
