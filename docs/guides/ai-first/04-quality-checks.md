# Quality Checks

Quality checks help catch problems before they cause issues. This guide explains what they are and how Claude handles them for you.

## What Are Quality Checks?

Quality checks are automated tools that examine your code for problems:

| Check | What It Does |
|-------|--------------|
| **Tests** | Run your code to make sure it works correctly |
| **Linting** | Find potential bugs and style issues |
| **Type checking** | Verify data types are used correctly |

Think of them like:
- **Spell check** - catches obvious mistakes
- **Grammar check** - finds structural problems
- **Fact check** - verifies things actually work

## Why They Matter

Quality checks catch problems that are easy to miss:

- A feature that worked yesterday but breaks today
- A typo that would cause an error for users
- Code that works but has a hidden bug

Running checks regularly keeps your code healthy and prevents surprises.

## Running Checks with Claude

### Run All Tests

```
Run the tests
```

Claude will run the test suite and tell you if everything passes or if something fails.

### Check for Problems

```
Are there any errors in my code?
```

```
Run the linter to check for issues
```

### Run Everything

```
Run all quality checks
```

This runs tests, linting, and type checking all at once.

### Check Specific Things

```
Run the tests for the user login feature
```

```
Check the contact form code for issues
```

## When Checks Fail

If something fails, Claude will explain what went wrong and usually fix it automatically.

**Example conversation:**

> **You:** Run the tests
>
> **Claude:** Two tests failed. The user registration test expects an email confirmation but we removed that feature. I'll update the test to match the current behavior.
>
> **Claude:** Fixed. All tests pass now.

If Claude can't fix it automatically, it will explain the issue and ask what you'd like to do.

## Quality Check Workflow

### Before Committing

Get in the habit of checking before you save:

```
Run all checks and fix any issues, then commit
```

Claude will:
1. Run all quality checks
2. Fix any problems it finds
3. Create the commit if everything passes

### After Making Changes

```
I just updated the login page - run the tests to make sure it still works
```

### Starting Your Day

```
Run the tests to make sure everything is working
```

## Understanding Results

### All Passing

```
✓ All 47 tests passed
✓ No linting errors
✓ Type checking passed
```

You're good to go!

### Something Failed

```
✗ 2 tests failed
  - test_user_can_login: Expected redirect to dashboard, got redirect to home
  - test_password_reset: Email not sent
```

Claude will explain what failed and either fix it or ask for guidance.

## The "Tarnished" System

This project uses a tool called "tarnished" that tracks which checks need to be re-run.

When you change code, relevant checks become "tarnished" (stale). After you run them and they pass, they become "clean" again.

You don't need to manage this yourself - Claude knows about it and will run checks when needed. But if you're curious:

```
Which checks need to be re-run?
```

## Tips

### Let Claude Handle It

You don't need to remember which checks to run. Just ask:

```
Make sure everything is working
```

Claude will run the appropriate checks.

### Fix As You Go

It's easier to fix one failing test than ten. Run checks regularly:

```
Run a quick check before we move on
```

### Before Creating a PR

Always verify everything works before creating a pull request:

```
Run all quality checks, fix any issues, then create a pull request
```

## Next Steps

You've completed the AI-First guides! You now know how to:

- [Create features](01-creating-features.md) by describing what you want
- [Fix bugs](02-fixing-bugs.md) by sharing error messages
- [Work with Git](03-working-with-git.md) to save and manage your code
- **Run quality checks** to keep your code healthy

For more advanced topics, check out the [Hands-On guides](../hands-on/) to learn about the underlying tools and commands.
