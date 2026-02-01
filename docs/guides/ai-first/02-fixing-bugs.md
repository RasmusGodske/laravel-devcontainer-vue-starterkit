# Fixing Bugs

Things will break sometimes - that's normal! When something goes wrong, Claude can help you figure out what happened and fix it.

## When You See an Error

Copy the error message and share it with Claude:

```
I'm seeing this error when I try to log in:

SQLSTATE[42S02]: Base table or view not found: 1146 Table 'app.users' doesn't exist

Can you fix it?
```

That's it. Claude will investigate, find the problem, and fix it.

## Describing Problems

If there's no error message, describe what's happening:

**What you were trying to do:**
```
I was trying to submit the contact form
```

**What happened instead:**
```
The page just refreshes and nothing happens. The message doesn't get saved.
```

**Where it happened:**
```
On the contact page at /contact
```

## Examples

**Page not loading:**
```
When I go to /dashboard, I just see a blank white page. It was working yesterday.
```

**Button not working:**
```
The "Save" button on the profile page doesn't do anything when I click it.
```

**Wrong data showing:**
```
The user list is showing the same user 5 times instead of different users.
```

**Styling issue:**
```
The navigation menu is covering the page content. I can't click on anything.
```

## Let Claude Investigate

Claude can check multiple things to find the problem:

- **Read error logs** - See what errors the server recorded
- **Check the code** - Find where the bug is
- **Run tests** - See if anything is failing
- **Check the database** - Verify data is correct

You don't need to ask for these specifically - just describe the problem and Claude will investigate.

## After the Fix

Claude will:
1. Explain what was wrong (in simple terms if you set up a non-technical profile)
2. Fix the issue
3. Run tests to make sure the fix works

You can then check it yourself in the browser at http://localhost:8080.

## If It's Still Broken

Sometimes the first fix doesn't completely solve the problem. Just tell Claude:

```
It's still not working. Now I'm seeing this error: [new error]
```

Or:

```
That fixed part of it, but now the form submits but I don't see a success message.
```

Claude will keep working on it.

## Preventing Future Issues

After fixing a bug, you can ask:

```
Can you add a test so this doesn't break again?
```

Claude will create an automated test that catches this problem if it ever comes back.

## Getting Help with Error Messages

If you see a scary-looking error and don't know what to do:

```
I'm seeing this error and I don't understand it:

[paste the error]

What does it mean and can you fix it?
```

Claude will explain what's happening and handle the fix.

## Next Steps

- [Working with Git](03-working-with-git.md) - Save your fixes
- [Quality Checks](04-quality-checks.md) - Keep your code healthy
