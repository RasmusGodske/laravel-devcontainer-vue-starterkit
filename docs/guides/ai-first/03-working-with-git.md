# Working with Git

This guide explains how your code is saved and backed up, and how to use Claude to manage it.

## What is Git?

Git tracks changes to your code and backs it up online. Think of it like:

- **Auto-save for your code** - every change is recorded
- **Cloud backup** - your code is safely stored on GitHub
- **Time machine** - you can always go back to earlier versions

## Two Places Your Code Lives

Your code exists in two places:

```
┌─────────────────┐                  ┌─────────────────┐
│                 │                  │                 │
│  Your Computer  │  ←── sync ───→   │     GitHub      │
│    (Local)      │                  │    (Remote)     │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
```

- **Local** - The code on your computer (in VS Code)
- **Remote** - The backup on GitHub (online)

You work on the local version, then sync it with GitHub to back it up.

## Three Things You Need to Know

### 1. Commit = Save a Snapshot

A **commit** saves your current changes with a description.

Think of it like saving a document, but Git remembers every save you've ever made.

**Tell Claude:**
```
Commit my changes
```

Or with a description:
```
Commit my changes - added a contact form
```

### 2. Push = Upload to GitHub

**Push** uploads your commits to GitHub so they're backed up online.

**Tell Claude:**
```
Push my changes to GitHub
```

### 3. Pull = Download from GitHub

**Pull** downloads any changes from GitHub to your computer.

**Tell Claude:**
```
Pull the latest changes
```

## Daily Workflow

### When You Start Working

```
Pull the latest changes
```

This makes sure you have the most recent version.

### As You Work

When you've made progress you want to save:

```
Commit my changes
```

### When You're Done for the Day

```
Push my changes to GitHub
```

This backs up your work online.

### All at Once

You can do everything in one go:

```
Commit my changes and push to GitHub
```

## Seeing What Changed

**What have I changed?**
```
What files have I changed since my last commit?
```

**What have I done recently?**
```
Show me my recent commits
```

**What changed in a specific commit?**
```
What did I change in the last commit?
```

## Undoing Mistakes

**Undo changes to a file (before committing):**
```
Discard my changes to the contact form file
```

**Undo all uncommitted changes:**
```
Discard all my uncommitted changes
```

**Undo the last commit:**
```
Undo my last commit
```

## Good Commit Messages

Commit messages help you remember what you did. Claude will write good messages for you, but you can also suggest your own:

**Good messages:**
- "Add contact form"
- "Fix login bug"
- "Update homepage design"

**Not helpful:**
- "Fix stuff"
- "Changes"
- "WIP"

## Let Claude Handle the Rest

Git has many advanced features (branches, merges, rebases, etc.). You don't need to learn these - just tell Claude what you want to accomplish:

```
I want to try something experimental without breaking my main code
```

```
I made some changes but I want to go back to yesterday's version
```

```
Someone else made changes, how do I get them?
```

Claude will handle the Git commands for you.

## Summary

| What You Want | Tell Claude |
|---------------|-------------|
| Save your changes | `Commit my changes` |
| Back up to GitHub | `Push to GitHub` |
| Get latest version | `Pull the latest changes` |
| See what changed | `What have I changed?` |
| Undo changes | `Discard my changes` |
| Undo last save | `Undo my last commit` |

## Next Steps

- [Quality Checks](04-quality-checks.md) - Keep your code healthy
